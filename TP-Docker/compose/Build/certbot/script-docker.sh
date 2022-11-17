#!/bin/bash -x
# -x permet de debugger

# vérification de la présence des variables nécessaires
if [ -z "${CERTBOT_NAME}" ] ; then
    echo "La variable CERTBOT_NAME n'existe pas"
    exit 1
fi
if [ -z "${CERTBOT_DOMAIN}" ]; then
    echo "La variable CERTBOT_DOMAIN n'existe pas"
    exit 1
fi
if [ -z "${CERTBOT_MAIL}" ]; then
    echo "La variable CERTBOT_MAIL n'existe pas"
    exit 1
fi
if [ -z "${CERTBOT_IP}" ]; then
    echo "La variable CERTBOT_IP n'existe pas"
    exit 1
fi


# calcul du nom de machine
FQDN="${CERTBOT_NAME}.${CERTBOT_DOMAIN}"

# formule magique qui trouve le répertoire contenant les certificats généré par let's encrypt
# on cherche par find un répertoire de letsencrypt qui contient le fichier de certificat
# puis on filtre selon le nom de domaine demandé (présent dans le nom du fichier)
# avant d'extraire le nom du répertoire
REPLENC=$(find /etc/letsencrypt/live/ -name cert.pem | grep ${FQDN} | xargs dirname)
# si cette variable est vide il n'y a pas de certificat
# sinon, il y en a un

if [ -z $REPLENC ];
then
    echo "Mon rep $REPLENC n'existe pas on demande le certificat"
    # A REMPLIR, il faut demander le nom DNS et générer le certificat

    # ========== Source OPENRC ==========
    source /usr/local/bin/openrc.sh

    # ========== Generate Token ==========
    # openstack token issue -f value -c expires

    # ========== Create DNS record =======
    openstack recordset create $CERTBOT_DOMAIN. --type A $CERTBOT_NAME --records $CERTBOT_IP

    # ========== Generate SSL/TLS Cert ==========
    certbot certonly \
    -n -manual-public-ip-logging-ok \
    --manual \
    --preferred-challenges=dns \
    --agree-tos \
    --manual-auth-hook /usr/local/bin/letsencrypt-designate \
    -m $CERTBOT_MAIL \
    -d $FQDN

else
    echo "Le repertoire $REPLENC existe alors on ne fait qu'un renouvellement"
    certbot renew
fi;
