#! /usr/bin/python3

import argparse

import sys
import os
import csv
#import ipdb
import testeur
import pandas
import json
import re
import uuid
import time
import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup



# Configuration
default_host = "localhost"
default_user = "ubuntu"

dockers = {}

nbOK = 0
nbNOK = 0

def ok(msg):
    global nbOK
    
    nbOK=nbOK+1
    print ("\033[48;5;100m\033[1m{}\033[0m\t{}".format("OK", msg))

def nok(msg):
    global nbNOK
    
    nbNOK=nbNOK+1
    print ("\033[48;5;196m\033[1m\33[5m{}\033[0m\t{}".format("Not OK", msg))

def traite_ok_temp(vok, mess):
    if (vok == 1):
        ok(mess)
    else:
        nok(mess)

def affiche_results(results):
    for result in results:
        traite_ok_temp(result[0], result[1])

def get_descript(t, iddocker):
    """
    Récupère une descrition d'un docker dont on a le nom a priori a partir
    de la commande docker inspect
    """
    sortie, err = t.test("sudo docker inspect {}".format(iddocker))
    if len(err) != 0:
        raise ValueError("Le docker {} n'existe pas".format(iddocker))
    descr = {}
    inspect = json.loads("".join(sortie))[0]

    descr['Name'] = inspect['Name']
    descr['HostnamePath'] = inspect['HostnamePath']
    descr['HostsPath'] = inspect['HostsPath']

    descr['Volumes'] = inspect['Mounts']
    descr['Ports'] = inspect['NetworkSettings']['Ports']
    descr['Networks'] = {}
    for net in inspect['NetworkSettings']['Networks'].keys():
        descr['Networks'][net] = {}
        descr['Networks'][net]['IPAddress'] = inspect['NetworkSettings']['Networks'][net]['IPAddress']
        descr['Networks'][net]['Prefix'] = inspect['NetworkSettings']['Networks'][net]['IPPrefixLen']
        descr['Networks'][net]['Aliases'] = inspect['NetworkSettings']['Networks'][net]['Aliases']

    descr['Env'] = inspect['Config']['Env']
    descr['ExtraHosts'] = inspect['HostConfig']['ExtraHosts']
    return descr

def change_status_docker(nom, status, t):
    r,e = t.test("docker {} {}".format(status, nom))
    if (len(e) != 0):
        print("La commande docker {} {} a occasionner l'erreur {}".format(status, nom, '\n'.join(e)))


def existance_fichiers(t, fichiers):
    manque = []
    for fich in fichiers:
        if not os.path.exists(fich):
            manque.append(fich)
    return manque

def test_install_docker(t):
    """
    test l'installation de docker, si le docker démon fonctionne et si
    le proxy est bien mis
    """
    sortie, err = t.test("sudo docker ps -a")
    if len(err) != 0:
        print("Il y a une erreur pour la commande docker ps")
        for l in err:
            print("\t\"{}\"".format(l))
        nok("Docker a un problème")
    else:
        ok("Docker semble installé et fonctionnel")



def test_presence_docker(t, dat):
    """
    teste si les dockers décrit par dat existent
    
    effet de bords : stocke la description des dockers utilisés dans un tableau et lance eventuellement une commande pour allumer les docker

    """
    sortie, err = t.test("sudo docker ps -a", result="file")
    sort = pandas.read_fwf(sortie,header=0)

    
    print("Dockers trouvés :\n");
    for l in sort['NAMES']:
        print("\t\"{}\"".format(l))

    dockers = {}
    bon = True
    for regexnom in dat.keys():
        # le docker est-il dans la liste des noms
        trouv = sort[sort['NAMES'].map(lambda x: bool(re.match(regexnom,x)))]
#        trouv = sort['NAMES'][nom == sort['NAMES']]
        if len(trouv) == 1:
            pos = trouv.index[0]
            nom = str(trouv.loc[pos,'NAMES'])
            ok("Docker \"{}\" trouvé en position {}".format(nom, pos))
            if (dat[regexnom]['changeStatus'] is not None):
                change_status_docker(nom, dat[regexnom]['changeStatus'], t)
            dockers[dat[regexnom]['service']] = get_descript(t, nom)
            if re.match("^{}.*$".format(dat[regexnom]['image']),sort['IMAGE'][pos]):
                 ok("Le nom de l'image est bien \"{}\"".format(sort['IMAGE'][pos]))
            else:
                 bon = False
                 nok("Le nom de l'image est \"{}\" et pas \"{}\""
                     .format(sort['IMAGE'][pos], dat[regexnom]['image']))
        elif len(trouv) > 1:
            bon = False
            nok("\"{}\" dockers trouvés pour la regex {}".format(len(trouv), regexnom))
            nok("Donc l'image n'est pas bonne non plus")
        else:
            bon = False
            nok("Docker \"{}\" non trouvé".format(regexnom))
            nok("Donc l'image n'est pas bonne non plus")

    return dockers

def verif_partage(vol, source, dest, moderw):
    print("vérifie le partage de {} sur {} en mode RW {}"
          .format(vol['Source'], vol['Destination'], vol['RW']))
    return ((re.match(source,vol['Source']))
            and (re.match(dest,vol['Destination']))
            and (vol['RW'] == moderw))
    

def verif_venv(Venvs, valeur, messageOK, messageNOK):
    try:
        if (any(map(lambda x: re.match(valeur, x), Venvs))):
            ok(messageOK)
            return True
    except:
        print("{} n'est pas iterable".format(Venvs))
    
    nok(messageNOK)
    return False
        
def verif_ip(docker, reseau, ip):
    if reseau in docker['Networks'].keys():
        if (docker['Networks'][reseau]['IPAddress'] == ip):
            ok("{} a bien l'adresse {} dans le réseau {}"
               .format(docker['Name'], ip, reseau)
            )
            return True
        else:
            nok("{} a l'adresse {} au lieu de {} dans le réseau {}"
               .format(docker['Name'],
                       docker['Networks'][reseau]['IPAddress'], ip, reseau))
            return False
    else:
        nok("{} n'a pas d'adresse dans le réseau {}"
            .format(docker['Name'], reseau))
        return False

def verif_alias(descr, reseau, alias):
    """
    Vérifie la présence d'alias réseau
    
    @param descr : la description où chercher
    @param reseau, alias : le réseau et l'alias à chercher
    @return : un résultat de rechercher (nbpoint, message)
    """
    if not (reseau in descr['Networks'].keys()):
        return (0, "le réseau {} n'est pas dans {}".format(reseau, descr['Name']))    
    if (alias in descr['Networks'][reseau]['Aliases']):
        return (1, "le docker {} a bien l'alias {} est dans le réseau {}".format(descr['Name'], alias, reseau))
    else:
        return (0, "le docker {} n'a pas l'alias {} dans le réseau {}".format(descr['Name'], alias, reseau))

def test_docktest(docker, t):
    nom = "base";
    passwd = "ppaasswwoorrdd";
    result, err = t.test("sudo cat '{}'".format(docker['HostnamePath']))
    if ((len(result)>0) and (result[0]=='{}\n'.format(nom))) :
        ok("Le hostname du docker est bien test")
    else:
        if (len(result)>0):
            nok("Le hostname du docker est {} au lieu de {}".format(result[0], nom))
        else:
            nok("Le hostname du docker n'existe pas")

    if (any(map(lambda x: x=="MYSQL_ROOT_PASSWORD={}".format(passwd), docker['Env']))):
        ok("on trouve la variable d'env pour le password de root")
    else:
        nok("Le mot de passe root ne semble pas bon")

    if (any(map(lambda x:
                verif_partage(x,
                              "/home/ubuntu/docker/data/base",
                              "/var/lib/mysql",
                              True
                ),
                docker['Volumes']))):
        ok("Le partage de données est trouvé")
    else:
        nok("Pas de partage pour les données")


    res, err = t.test('ls /home/ubuntu/docker/data/base/')
    if (any(map(lambda x: x=='A_BASE\n', res))):
        ok("On trouve la base A_BASE")
    else:
        print('les fichiers du partage "/home/ubuntu/docker/data/base/" sont ')
        for f in res:
            print ("  - {}".format(f))
        nok("On ne trouve la base A_BASE")

    res, err = t.test('ls /home/ubuntu/docker/data/base/')
    if (any(map(lambda x: x=='B_BASE\n', res))):
        ok("On trouve la base B_BASE")
    else:
        print('les fichiers du partage "/home/ubuntu/docker/data/base/" sont ')
        for f in res:
            print ("  - {}".format(f))
        nok("On ne trouve la base B_BASE")

    return True

    
def test_dockbdd(docker, t):
    nom = "basededonnee"
    result, err = t.test("sudo cat '{}'".format(docker['HostnamePath']))
    if ((len(result)>0) and (result[0]=='{}\n'.format(nom))) :
        ok("Le hostname du docker est bien test")
    else:
        if (len(result)>0):
            nok("Le hostname du docker est {} au lieu de {}".format(result[0], nom))
        else:
            nok("Le hostname du docker n'existe pas")

    print("Vérification des variables d'environement")
    venvs = [
        ["MYSQL_ROOT_PASSWORD=ppaasswwoorrdd", "On trouve le mot de passe root", "Le mot de passe root n'est pas bon"],
        ["MYSQL_USER=userwordpress","On trouve l'utilisateur wordpress", "On ne trouve pas l'utilisateur wordpress"],
        ["MYSQL_PASSWORD=passwordpress","MdP de wordpress", "mauvais MdP pour wordpress"],
        ["MYSQL_DATABASE=wordpress","La base de donnée wordpress est là", "Pas la base de donnée wordpress"]
    ]
    for ve in venvs:
        verif_venv(docker["Env"], ve[0], ve[1], ve[2])

    if (any(map(lambda x:
                verif_partage(x,
                              "/home/ubuntu/docker/data/base8",
                              "/var/lib/mysql",
                              True
                ),
                docker['Volumes']))):
        ok("Le partage de données est trouvé")
    else:
        nok("Pas de partage pour les données")



    res, err = t.test('ls /home/ubuntu/docker/data/base8/')
    if (any(map(lambda x: x=='wordpress\n', res))):
        ok("On trouve la base wordpress")
    else:
        print('les fichiers du partage "/home/ubuntu/docker/data/base8/" sont ')
        for f in res:
            print ("  - {}".format(f))
        nok("On ne trouve la base wordpress")

    verif_ip(docker, "resTP", "172.18.10.100")

    bon, mess = verif_alias(docker, "resTP", "bdd")
    if (bon):
        ok(mess)
    else:
        nok(mess)

        
    return True
    
def test_dockpma(docker, t):

    print("Vérification des variables d'environement")
    venvs = [
        ["PMA_HOST=(bdd|serv-bdd)", "La base est bien configurée", "La base de donnée n'est pas bien configurée le serveur doit être nomé 'bdd' ou 'serv-bdd'"],
        ["PMA_ABSOLUTE_URI=(http://192.168.[0-9]+.[0-9]+)?/pma/?","L'url d'accès est bonne pour nginx", "L'url d'accès n'est pas bonne pour nginx"],
    ]
    for ve in venvs:
        verif_venv(docker["Env"], ve[0], ve[1], ve[2])


    verif_ip(docker, "resTP", "172.18.10.101")
    # verif_venv(docker["ExtraHosts"], "bdd:172.18.100.10",
    #            "La liaison avec la bdd est bonne",
    #            "La liaison avec la bdd n'est pas bonne"
    # )

    bon, mess = verif_alias(docker, "resTP", "pma.tpcloud")
    if (bon):
        ok(mess)
    else:
        nok(mess)


    res, err = t.test("wget --no-proxy http://172.18.10.101 -O -")
    if (any(map(lambda x: re.search("HTTP request sent, awaiting response... 200 OK",x), err))):
        ok("serv-madm semble répondre")
    else:
        nok("serv-madm ne semple pas répondre")

    bon = False
    for lig in res:
        m = re.search("CommonParams", lig)
        if (m):
            ok("serv-madm semble être un docker phpMyAdmin")
            m1 = re.search('rootPath:"([^"]*)"', lig)
            if (re.match("/?pma/?",m1.group(1))):
                ok("le rootpath est bien {}".format(m1.group(1)))
            else:
                nok("le rootpath est {}".format(m1.group(1)))
            bon=True
    if (not bon):
        nok("serv-madm ne semble pas être un docker phpMyAdmin")
        
        
    

def test_docknginx(docker, t):

    verif_ip(docker, "resTP", "172.18.10.105")
    # verif_venv(docker["ExtraHosts"], "(dock)?pma:172.18.100.11",
    #            "La liaison avec pma est bonne",
    #            "La liaison avec pma n'est pas bonne (la machine doit s'appeléer pma ou dockpma"
    # )
    if (any(map(lambda x:
                verif_partage(x,
                              "/home/ubuntu/docker/conf/nginx\.conf",
                              "/etc/nginx/nginx.conf",
                              False
                ),
                docker['Volumes']))):
        ok("Le partage de configuration est trouvé")
    else:
        nok("Pas partage de configuration")

    if (any(map(lambda x:
                verif_partage(x,
                              "/home/ubuntu/docker/data/nginx/?",
                              "/www/?",
                              True
                ),
                docker['Volumes']))):
        ok("Le partage de site trouvé")
    else:
        nok("Pas partage de site")

    res, err = t.test("wget --no-proxy http://localhost/pma/ -O -")
    if (any(map(lambda x: re.search("HTTP request sent, awaiting response... 200 OK",x), err))):
        ok("pma semble répondre via nginx semble répondre")
    else:
        nok("serv-madm ne semple pas répondre via nginx")

    bon = False
    for lig in res:
        m = re.search("CommonParams", lig)
        if (m):
            ok("serv-madm semble être un docker phpMyAdmin")
            m1 = re.search('rootPath:"([^"]*)"', lig)
            if (re.match("/?pma/?",m1.group(1))):
                ok("le rootpath est bien {}".format(m1.group(1)))
            else:
                nok("le rootpath est {}".format(m1.group(1)))
            bon=True
    if (not bon):
        nok("serv-madm ne semble pas être un docker phpMyAdmin")


def test_dockwordpress(docker, ipVM, t):
    #nettoye_session_owc(t, docker['Name'])

    venvs = [
        ["WORDPRESS_DB_NAME=wordpress",
         "La base de données est connue",
         "La base de données n'est pas bonne"],
        ["WORDPRESS_DB_HOST=bdd",
         "Le serveur de base de données est configuré",
         "Le serveur de base de données n'est pas configuré"],
        ["WORDPRESS_DB_USER=userwordpress",
         "L'utilisateur de base de données est configuré",
         "L'utilisateur de base de données n'est pas configuré"],
    ]
    for ve in venvs:
        verif_venv(docker["Env"], ve[0], ve[1], ve[2])

    
    
    if (any(map(lambda x:
                verif_partage(x,
                              "/home/ubuntu/docker/php/?",
                              "/var/www/html/?",
                              True
                ),
                docker['Volumes']))):
        ok("Le partage de fichiers de données est trouvé")
    else:
        nok("Pas partage de fichiers de données")

    res, mess = verif_alias(docker, 'resTP', 'wordpress')
    traite_ok_temp(res, mess)

    

    
def verif_ping(t, dockfrom, to, expect):
    com = "docker exec -t {} ping -c 3 {}".format(dockfrom, to)
    res, err = t.test(com)
    if (len(err)>0):
        print("La commande {} stop à générée l'erreur {}"
              .format(com, " ".join(err)))
        return (0, "Impossible de faire un ping")
    address = None
    for lig in res:
        m = re.match(".*[0-9]+ bytes from ([0-9.]+): .*seq=[0-2] ttl=64 time=[0-9.]+ .*", lig)
        if (m):
            address = m.group(1)
            break
    if (address is None):
        return (0, "Aucun ping ne passe entre {} et {} cela donne {}".format(dockfrom, to, " ".join(res)))
    
    if (address == expect):
        return (1, "Un ping au moins fonctionne entre {} et {}".format(dockfrom, to))
    else:
        return (0, "Un ping au moins fonctionne entre {} et {} mais avec une mauvaise adresse".format(dockfrom, to))
        


        
def test_all(server="localhost", user=None, key=None, parts = ["debut", "owncloud"]):
    global nbOK
    global nbNOK
    
    nbOK=0
    nbNOK=0
    
    if server == "localhost":
        t = testeur.testeur()
    else:
        t = testeur.testeur_ssh(server, user, key=key)

    #    test_install_docker(t)

    if (('debut' in parts)
        or ('nextcloud' in parts)):

        
        # res, err = t.test("docker-compose -f /home/ubuntu/compose/docker-compose.yml stop")
        # if (len(err)>0):
        #     print("La commande docker-compose stop à générée l'erreur {}"
        #           .format(" ".join(err)))
        # res, err = t.test("docker start dockbase dockNextcloud dockMyAdm dockFront")
        # if (len(err)>0):
        #     print("La commande docker start à générée l'erreur {}"
        #           .format(" ".join(err))  )  
        
        dat = {
            'serv-mysql'    : {'image': 'mysql:5.*'  , 'changeStatus':'stop'  , 'service': 'serv-mysql'}, 
            'serv-bdd'     : {'image': 'mysql:8.*'  , 'changeStatus':'start' , 'service': 'serv-bdd'},
            'serv-madm'     : {'image': 'phpmyadmin'    , 'changeStatus':'start' , 'service': 'serv-madm'},
            'serv-nginx'   : {'image': 'nginx'         , 'changeStatus':'start' , 'service': 'serv-nginx'},
            'serv-wordpress': {'image': 'wordpress-perso', 'changeStatus':'start' , 'service': 'serv-wordpress'},
        }
    
        dockers = test_presence_docker(t, dat)
        #verifie_docker(t)

    if ('debut' in parts):
        print("####################################")
        print("## Vérification du docker serv-mysql ##")
        print("####################################")
        if ('serv-mysql' in dockers.keys()):
            test_docktest(dockers['serv-mysql'], t)
        print("####################################")
        print("## Vérification du docker serv-bdd ##")
        print("####################################")
        if ('serv-bdd' in dockers.keys()):
            test_dockbdd(dockers['serv-bdd'], t)
        print("####################################")
        print("## Vérification du docker serv-madm ##")
        print("####################################")
        if ('serv-madm' in dockers.keys()):
            test_dockpma(dockers['serv-madm'], t)
        print("####################################")
        print("## Vérification du docker serv-nginx ##")
        print("####################################")
        if ('serv-nginx' in dockers.keys()):
            test_docknginx(dockers['serv-nginx'], t)

    if ('wordpress' in parts):
        print("#########################################")
        print("## Vérification du docker serv-wordpress ##")
        print("#########################################")
        if ('serv-wordpress' in dockers.keys()):
            test_dockwordpress(dockers['serv-wordpress'], server, t)

    if ('compose' in parts):
        print("#########################################")
        print("## Vérification des compose ##")
        print("#########################################")
        # res, err = t.test("docker stop docknginx dockbdd dockpma dockowncloud")
        # if (len(err)>0):
        #     print("La commande docker stop start à générée l'erreur {}"
        #           .format(" ".join(err))  )
        trouv = False
        nomrep = "compose"
        pathcompose = "/home/ubuntu/{}".format(nomrep)
        print("On test avec le nom '{}'".format(nomrep))
        res, err = t.test("cat {}/docker-compose.yml".format(pathcompose))
        if (len(err)==0):
            trouv = True
        else:
            nomrep="ComposeNext"
            pathcompose = "/home/ubuntu/{}".format(nomrep)
            print("On test avec le nom '{}'".format(nomrep))
            res, err = t.test("cat {}/docker-compose.yml".format(pathcompose))
            if (len(err) == 0):
                trouv = True
        
        if (not trouv):
            print("On essaye un find")
            trouv = False
            res, err = t.test("find /home/ubuntu/ -name docker-compose.yml".format(nomrep))
            print ("On atrouve {}".format(res))
            if (len(err)==0) and (len(res)==1):
                fichier = re.sub("[^-._a-zA-Z0-9/]", "", res[0])
                print("Fichier = {}".format(fichier))
                m = re.match("(.*/([a-zA-Z0-9]+)/)docker-compose.yml", fichier)
                if (m):
                    pathcompose = m[1]
                    nomrep = m[2]
                    trouv = True
            else:
                print("Le find a généré l'erreur {}".format(err))
        if not trouv:
            raise Exception("Le compose n'est pas trouvé")
        else:
            print("Le compose est là {} et le nom du repertoire {}".format(pathcompose, nomrep))
        
        res, err = t.test("docker-compose -f {}/docker-compose.yml up -d".format(pathcompose))
        if (len(err)>0):
            print("La commande docker-compose start à générée l'erreur {}"
              .format(" ".join(err)))

        dat = {
            '{}_base_.*'.format(nomrep.lower())      : {'image': 'mysql:5.7.27'    , 'changeStatus':None, 'service': 'mysql'}, 
            '{}_myadm_.*'.format(nomrep.lower()) : {'image': 'phpmyadmin'      , 'changeStatus':None, 'service': 'phpmyadmin'}, 
            '{}_nginx_.*'.format(nomrep.lower())      : {'image': 'nginx'           , 'changeStatus':None, 'service': 'nginx'},
            '{}_nextcloud_.*'.format(nomrep.lower())   : {'image': '{}_nextcloud'.format(nomrep.lower()), 'changeStatus':None, 'service': 'nextcloud'},
            '{}_onlyoffice_.*'.format(nomrep.lower()) : {'image': 'onlyoffice', 'changeStatus':None, 'service': 'onlyoffice'},
        }
        dockers = test_presence_docker(t, dat)
        test_compose_aliases(t, dockers, nomrep.lower())
        if ('nextcloud' in dockers.keys()):
            test_compose_nextcloud(t, dockers['nextcloud'], server, nomrep.lower(), pathcompose)
        
    t.close()
    return (nbOK,nbNOK)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Passe des scripts de test à distance ou en local")
    parser.add_argument("-s", "--server", type=str, dest="server", default=default_host, help="La machine sur laquelle se connecter")
    parser.add_argument("-u", "--user", type=str, dest="user",
                        default=default_user, help="Le nom de l'utilisateur pour se connecter sur la machine (n'est pas considéré pour la machine locale")
    parser.add_argument("-k", "--key", type=str, dest="key", default=None, help="nom du fichier de clef")

    parser.add_argument("parts", type=str, metavar="part", nargs='+', 
                        help="Parties de la vérification à faire debut, owncloud ou compose."
                            +"Il ne faut pas utiliser compose avec les autres")
    
    args = parser.parse_args()

    print("##################################")
    print("##################################")
    print("Test du serveur {} pour {}".format(args.server, " ".join(args.parts)))
    print("##################################")
    print("##################################")
    
    nbok, nbnok = test_all(args.server, args.user,args.key, args.parts)
    print ("## Au final {}/{}".format(nbOK, nbOK+nbNOK))
    
