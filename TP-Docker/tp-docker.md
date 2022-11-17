---
tags: [TP, Docker]
aliases: ["CSV - TP1 sur Docker", "TP1 sur Docker - CSV"]
---

# TP1 - Cloud & Virtualisation - Docker

Pre-requisites
---

1) Créer une VM sur la plateforme OpenStack du département

Pour se connecter:
```bash
ssh ubuntu@192.168.246.47 -i .ssh/cloud-virt-tp1.key
```

Container mysql (docktest)
---

### Q - Les 3 images `mysql` mieux notés

```bash
docker search mysql
```

Les 3 mieux notés sont:
- mysql
- mariadb
- phpmyadmin

### Q - Quelles sont les versions proposées et comment reconnait-on la dernière ?

Les versions (ou les tags) proposées sont: `8.0`, `8.0.30`, `8.0-oracle`, `8.0.30-debian`, etc. /
La dernière correpond au tag `latest`.

### Q - Sur quelle distribution est basée la version 5 de mysql ?

Les distributions disponibles pour la version `5` de `mysql` sont: `debian` et `oracle`.

### Télécharger la dernière image de la version 5

Pull la dérnière version `5` de `mysql`:

```bash
docker pull mysql:5.7.39
```

`docker images` pour lister les images installées:

```log
REPOSITORY  TAG     IMAGE ID      CREATED       SIZE
mysql       5.7.39  daff57b7d2d1  3 weeks ago   430MB
```

- Le nom: mysql
- Le tag: 5.7.39

### Créer et lancer un **container** à partir de l'**image** installée

```bash
docker run -d \
--name docktest \
--hostname test \
-e MYSQL_ROOT_PASSWORD=Adm1nP@ssw0rd \
mysql:5.7.39
```

-   Grâce à la commande `docker inspect` trouver l'adresse attribuée au container:
`d2d878e1c5b5da27a3daed0b526e2d1e934d7168709215791bc28678287e5888`

Pour générer le PWD **aléatoirement**, le param `MYSQL_RANDOM_ROOT_PASSWORD`: (et sans l'option `-d` pour afficher le mot de passe généré)

```bash
docker run \
--name docktest \
--hostname test \
-e MYSQL_RANDOM_ROOT_PASSWORD=yes \
mysql:5.7.39
```

Dans l'output:
```log
[Note] [Entrypoint]: GENERATED ROOT PASSWORD: i5IYESTWFaygbFUVRYba9AmbWC4Z7hMK
```

### Q - Se connecter sur le serveur mysql avec `telnet` et `mysql`

La commande `docker inspect docktest` affiche un json. \
Dans *NetworkSettings*: `"IPAddress": "10.247.0.2"`

- Connexion via **telnet**: `telnet 10.247.0.2 3306`

  ```log
  Trying 10.247.0.2...
  Connected to 10.247.0.2.
  Escape character is '^]'.
  J
  5.7.39☻▼▬|-l9∟↓☻§♦i
  <P☺[9X‼]]mysql_native_passwordConnection closed by foreign host.
  ```

- Connexion avec `mysql` via **docker exec**:
  ```bash
  docker exec -it docktest mysql -u root -pi5IYESTWFaygbFUVRYba9AmbWC4Z7hMK
  ```

  > **! Attention !** Il n'y a pas d'espace après l'option `-p`

### Q - Créer un fichier dans le container avec `docker exec`

```bash
docker exec -it docktest touch /toto && echo "coucou" > /toto
```

La commande ci-dessus **échoue à cause des droits insuffisants**:

```log
-bash: /toto: Permission denied
```

Résolution:

- Mettre les quotes (`'command'`) autour de la commande:
  ```bash
  docker exec -it docktest 'touch /toto && echo "coucou" > /toto'
  ```
  -> toujours des problèmes.

- Utiliser l'option `sh -c <command>` à la place:
  ```bash
  docker exec -it docktest sh -c 'echo "coucou" > /toto'
  ```

Pour vérifier si le fichier a été bien créé:
```bash
docker exec -it docktest sh -c 'ls -la / | grep toto'
```

### Q - Data `docker inspect docktest`

```bash
docker inspect docktest
```

```json
"Data": {
  "LowerDir": "/var/lib/docker/overlay2/9ab4771e2f698f778cf5363857f88862503cb5763b37f0d23549cbf2ecc3078c-init/diff:/var/lib/docker/overlay2/48857dfe9031620872d14591dca141d0cda513140523ef3cdaf7aef7f0cd474f/diff:/var/lib/docker/overlay2/383137f9b573329922109c0163afe6dd243258b35416e96ed79888596f9719df/diff:/var/lib/docker/overlay2/c40f9d62bf511f0f1899b97cfb6a963792df5d88a7e3adb8b157d75cb099f083/diff:/var/lib/docker/overlay2/a41f6afbfb5d43bde900d765caadc806887143c6bbc828b07539e935442ba959/diff:/var/lib/docker/overlay2/7f1cf87a9bca7af13c9dde7605b77bafc895c5fea2d1e58a623e612e35c6e6f9/diff:/var/lib/docker/overlay2/1d4fe4ae8e28ee42c32409042ed2d548b2855a1aaef15a6d808d5614c7215e75/diff:/var/lib/docker/overlay2/28762d4e34240fb74aa956cecad75edb913f676fdf5edadaaf476003e4111c3d/diff:/var/lib/docker/overlay2/d78282c1b4859ca4fcb0b8ac190d1a92c7653e5c144862735a6266313e43c52e/diff:/var/lib/docker/overlay2/518886a23a7cacbdc425f40162de99f38ea295be7e5b2701ddc4dbdbf250a735/diff:/var/lib/docker/overlay2/83eccef5a52903684fbb3503d28f98d1a20fcbbdcc9aadf7c281c0813ca582e6/diff:/var/lib/docker/overlay2/c560c92c481ca680a110d9cb57e63e0e4bfb9d22cbf1505b0d9fb841f2f1b04c/diff",
  "MergedDir": "/var/lib/docker/overlay2/9ab4771e2f698f778cf5363857f88862503cb5763b37f0d23549cbf2ecc3078c/merged",
  "UpperDir": "/var/lib/docker/overlay2/9ab4771e2f698f778cf5363857f88862503cb5763b37f0d23549cbf2ecc3078c/diff",
  "WorkDir": "/var/lib/docker/overlay2/9ab4771e2f698f778cf5363857f88862503cb5763b37f0d23549cbf2ecc3078c/work"
},
"Name": "overlay2"
```

- **LowerDir**: read-only directories for Docker container
- **UpperDir**: read-write dirs for Docker container
- **MergedDir**: directory for `chroot` command when running a Docker container
- **WorkDir**: working directory

Container mysql avec un volume partagé
---

L'ordre des paramètres de l'option `-v` est `<HOST_DIR>`:`<CONTAINER_DIR>`

```bash
docker run -d \
--name serv-mysql \
--hostname base \
-e MYSQL_ROOT_PASSWORD=ppaasswwoorrdd \
-v /home/ubuntu/docker/data/base/:/var/lib/mysql \
mysql:5.7.39
```

Créer une base de données
```bash
docker exec -it serv-mysql sh -c "mysql -u root -pppaasswwoorrdd -e 'CREATE DATABASE A_BASE;'"
```

Vérifier si la BD a été bien créée
```bash
docker exec -it serv-mysql sh -c "mysql -u root -pppaasswwoorrdd -e 'SHOW DATABASES;'"
```

Un repertoire **"A_BASE"** a été créé dans le dossier hote `/home/ubuntu/docker/data/base/`

```log
drwxr-x--- 2 systemd-coredump systemd-coredump     4096 Sep 19 12:38 A_BASE
```

Docker *phpMyAdmin*
---

**Q:** Peut-on ajouter phpMyAdmin au docker mysql pour former un docker avec le serveur et l'interface. Si oui pourquoi ne le fait-on pas ? \
**R:** Oui, mais on ne le fait pas pour séparer les deux environnements.

```bash
docker search phpMyAdmin
```

```log
NAME                    DESCRIPTION                                     STARS OFFICIAL AUTOMATED
phpmyadmin/phpmyadmin   A web interface for MySQL and MariaDB.          1167           [OK]
phpmyadmin              phpMyAdmin - A web interface for MySQL and M…   628   [OK]
```

Créer un réseau
```bash
docker network create \
--subnet=172.18.10.0/24 \
resTP
```

Créer un container *serv-bdd* (mysql)
```bash
docker run -d \
--name serv-bdd \
--hostname basededonnee \
-e MYSQL_ROOT_PASSWORD=ppaasswwoorrdd \
-v /home/ubuntu/docker/data/base/:/var/lib/mysql \
--net=resTP \
--ip=172.18.10.100 \
--network-alias=bdd \
mysql:5
```

Container *phpMyAdmin*
---

Créer un container *phpMyAdmin*
```bash
docker run -d \
--name serv-madm \
-p 8080:80 \
-e PMA_HOST=bdd \
--net=resTP \
--ip=172.18.10.101 \
--network-alias=pma \
phpmyadmin/phpmyadmin:latest
```

Après la création, `docker container ls -a`:
```log
CONTAINER ID   IMAGE                          COMMAND                  CREATED          STATUS                    PORTS                                   NAMES
c924188919a0   phpmyadmin/phpmyadmin:latest   "/docker-entrypoint.…"   28 seconds ago   Up 23 seconds             0.0.0.0:8080->80/tcp, :::8080->80/tcp   serv-madm
c488a23cd7d1   mysql:5                        "docker-entrypoint.s…"   16 minutes ago   Up 16 minutes             3306/tcp, 33060/tcp                     serv-bdd
b6b37757c13a   mysql:5.7.39                   "docker-entrypoint.s…"   11 hours ago     Exited (0) 11 hours ago                                           serv-mysql
```

Les commandes `docker inspect serv-bdd` et `docker inspect serv-madm` donnent le même résultat:
```json
"Networks": {
  "resTP": {
    "IPAMConfig": {
      "IPv4Address": "172.18.10.100"
    },
    "Links": null,
    "Aliases": [
      "bdd",
      "c488a23cd7d1",
      "basededonnee"
    ],
    "NetworkID": "4bad34b2e9ac50567cdc8feaef487cd39bb1dc5e681faa20bb947cad07b0b848",
    "EndpointID": "10d7d40745b55b9a513b94b4fac0887590f9d21f9608bf7d65d64b00333135bd",
    "Gateway": "172.18.10.1",
    "IPAddress": "172.18.10.100",
    "IPPrefixLen": 24,
    "IPv6Gateway": "",
    "GlobalIPv6Address": "",
    "GlobalIPv6PrefixLen": 0,
    "MacAddress": "02:42:ac:12:0a:64",
    "DriverOpts": null
  }
}
```

En suivant le lien http://192.168.246.47:8080, on peut se connecter via `phpMyAdmin`

Pour se connecter en tant qu'administrateur:
- login: `root`
- mdp: `ppaasswwoorrdd` (créé avant)

Après la création d'une nouvelle base de données `B_BASE`, on constate qu'un nouveau repertoire nommé également `B_BASE` a été créé dans le dossier partagé `~/docker/data/base`
```bash
drwxr-x--- 2 systemd-coredump systemd-coredump     4096 Sep 20 00:05 B_BASE
```

**Q:** La VM peut-elle contacter ces dockers ? Une autre VM le peut-elle ? \
**R:** Oui, elle peut, mais pas l'inverse. Une autre VM ne peut pas contacter les dockers directement, mais il est possible de se connecter via l'interface web *phpMyAdmin*.

```log
drwxr-x--- 2 systemd-coredump systemd-coredump     4096 Sep 20 00:11 C_BASE
```

Configuration des dockers
---

### Container *nginx*

Créer le container
```bash
docker run -d \
--name serv-nginx \
-p 80:80 \
--net=resTP \
--ip=172.18.10.105 \
-v /home/ubuntu/nginx.conf:/etc/nginx/nginx.conf:ro \
-v /home/ubuntu/docker/data/nginx/:/www/ \
nginx:latest
```

Vérfier l'installation avec `docker container ls -a`:
```bash
CONTAINER ID   IMAGE                          COMMAND                  CREATED          STATUS                    PORTS                                   NAMES
d3970f9b8706   nginx:latest                   "/docker-entrypoint.…"   10 seconds ago   Up 7 seconds              0.0.0.0:80->80/tcp, :::80->80/tcp       serv-nginx
```

Pour pouvoir utiliser la commande suivante:
```bash
echo "voir <a href='/pma/'>phpMyAdmin</a>" > /home/ubuntu/docker/data/nginx/index.html
```

> Il faut changer les droits du repertoire `~/docker/` recursivement, car au moment de bind des dossiers, le dossier `~/docker/` n'existait pas encore et a ete cree par `root`.

On change les droits:
```bash
sudo chown -R ubuntu:ubuntu ~/docker/
```

Maintenant on va pouvoir utiliser la commande en tant qu'`ubuntu`:
```bash
echo "voir <a href='/pma/'>phpMyAdmin</a>" > /home/ubuntu/docker/data/nginx/index.html
```

> L'index sur serveur web est toujours celui par defaut (*"Welcome to nginx! ..."*), car dans la config d'`nginx` la racine est `/usr/share/nginx/html`. Ainsi, on ne voit pas la nouvelle page *index*.

On change la racine dans la config d'`nginx`, set ```root /www/;```

Pour appliquer les changements il faut restart `nginx`:
```bash
docker stop serv-nginx
docker start serv-nginx
```
Ou
```bash
docker restart serv-nginx
```

Ajouter une directive `location` dans la config du serveur `nginx`:
```nginx
location /pma/ {
  proxy_pass http://pma/;
}
```

> Ici `pma` est un alias (sur le reseau `resTP`) du container `serv-madm` qu'on va re-creer. 

Reconstruire le container *phpMyAdmin*:
```bash
docker stop serv-madm
docker rm serv-madm

docker run -d \
--name serv-madm \
-e PMA_HOST=bdd \
-e PMA_ABSOLUTE_URI=http://192.168.246.47/pma/ \
--net=resTP \
--ip=172.18.10.101 \
--network-alias=pma \
phpmyadmin/phpmyadmin:latest
```

Restart `nginx`:
```bash
docker stop serv-nginx
docker start serv-nginx
```

Container Wordpress
---

Re-créer un container *serv-bdd* (mysql)
```bash
docker stop serv-bdd
docker rm serv-bdd

docker run -d \
--name serv-bdd \
--hostname basededonnee \
-e MYSQL_ROOT_PASSWORD=ppaasswwoorrdd \
-e MYSQL_USER=userwordpress \
-e MYSQL_PASSWORD=passwordpress \
-e MYSQL_DATABASE=wordpress \
-v /home/ubuntu/docker/data/base8/:/var/lib/mysql/ \
--net=resTP \
--ip=172.18.10.100 \
--network-alias=bdd \
mysql:8
```

Créer et lancer un container *Wordpress*
```bash
docker run -d \
--name serv-wordpress \
-e WORDPRESS_DB_HOST=bdd \
-e WORDPRESS_DB_USER=userwordpress \
-e WORDPRESS_DB_PASSWORD=passwordpress \
-e WORDPRESS_DB_NAME=wordpress \
-v /home/ubuntu/docker/data/wordpress/:/var/www/html/ \
--net=resTP \
--ip=172.18.10.107 \
--network-alias=wordpress \
-p 8080:80 \
wordpress:latest
```

Ajouter des headers au proxy sur la route par defaut (`/`):
```nginx
location / {
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_pass http://wordpress_backend/;
}
```
C'est necessaire pour pouvoir acceder aux scripts js et styles css de `wordpress`.

Création d'une première image
---

Créer une image à partir du Dockerfile fourni:
```bash
docker build \
-t wordpress-perso:0.1 \
- < Dockerfile
```

Re-créer et lancer le container `serv-wordpress`:
```bash
docker stop serv-wordpress
docker rm serv-wordpress

docker run -d \
--name serv-wordpress \
-e WORDPRESS_DB_HOST=bdd \
-e WORDPRESS_DB_USER=userwordpress \
-e WORDPRESS_DB_PASSWORD=passwordpress \
-e WORDPRESS_DB_NAME=wordpress \
-v /home/ubuntu/docker/php/:/var/www/html/ \
--net=resTP \
--ip=172.18.10.107 \
--network-alias=wordpress \
-p 8080:80 \
wordpress-perso:0.1
```

> Maintenant, en allant sur http://192.168.246.47/, on constate que la page affichée est celle qui propose choisir une langue.

Ajouter la ligne suivante au `Dockerfile`:
```Dockerfile
COPY uploads.ini /usr/local/etc/php/conf.d/
```

> **! ATTENTION !** Le chemin du fichier à copier est relatif au repertoire du Dockerfile. 

> **! ATTENTION !** If you build using STDIN (`docker build - < somefile`), there is no build context, so `COPY` can’t be used. 

Créer une nouvelle image à partir du Dockerfile:
```bash
docker build \
-t wordpress-perso:0.2 \
-t wordpress-perso:latest \
.
```

Re-créer et lancer le container `serv-wordpress` **sans préciser de version**:
```bash
docker stop serv-wordpress
docker rm serv-wordpress

docker run -d \
--name serv-wordpress \
-e WORDPRESS_DB_HOST=bdd \
-e WORDPRESS_DB_USER=userwordpress \
-e WORDPRESS_DB_PASSWORD=passwordpress \
-e WORDPRESS_DB_NAME=wordpress \
-v /home/ubuntu/docker/php/:/var/www/html/ \
--net=resTP \
--ip=172.18.10.107 \
--network-alias=wordpress \
-p 8080:80 \
wordpress-perso
```

Get the hash of the image via `docker inspect serv-wordpress | grep Image`:
```json
{
  [
    "Image": "sha256:fba779a63b6ed2024b061e5acfcc1a29938d4b674956bfce7783208177049437",
      "Image": "wordpress-perso"
  ]
}
```

Compare with the hash using `docker images`:
```log
REPOSITORY              TAG       IMAGE ID       CREATED          SIZE
wordpress-perso         0.2       fba779a63b6e   4 minutes ago    636MB
wordpress-perso         latest    fba779a63b6e   4 minutes ago    636MB
```

Terminer l'installation de *wordpress*
---

En utilisant l'outil [wp-cli](https://developer.wordpress.org/cli/commands/core/install/) dockerisé (`wordpress:cli`, un exemple d'utilisation est disponible [en bas de la page officielle du container docker](https://hub.docker.com/_/wordpress)), lancer une installation de site:
```bash
docker run -it --rm \
--volumes-from serv-wordpress \
--network=resTP \
-e WORDPRESS_DB_HOST=bdd \
-e WORDPRESS_DB_USER=userwordpress \
-e WORDPRESS_DB_PASSWORD=passwordpress \
-e WORDPRESS_DB_NAME=wordpress \
wordpress:cli \
wp core install \
--url=http://192.168.246.47/ \
--title="Mon Site Wordpress" \
--admin_user=lemaitre \
--admin_password=ppaasswwoorrdd \
--admin_email=monmail@univ-lyon1.fr \
--skip-email
```

- `--rm` supprime le container apres l'execution de la commande

Output:
```log
Success: WordPress installed successfully.
```

Reconstruire le container *phpMyAdmin*: (a cause des modifs du sujet de TP).
```bash
docker stop serv-madm
docker rm serv-madm

docker run -d \
--name serv-madm \
-e PMA_HOST=bdd \
-e PMA_ABSOLUTE_URI=http://192.168.246.47/pma/ \
--net=resTP \
--ip=172.18.10.101 \
--network-alias=pma.tpcloud \
phpmyadmin/phpmyadmin:latest
```
- Network alias: pma -> pma.tpcloud

Mettre à jour la config nginx:
```nginx
location /pma/ {
  proxy_pass http://pma.tpcloud/;
}
```

Restart `nginx`:
```bash
docker restart serv-nginx
```

Docker-compose
---

### Installation

Installed the Docker Compose **plugin**, via setting up the official repository and installing via `apt install docker-compose-plugin`.

Check the installation using `docker compose version`:
```bash
Docker Compose version v2.10.2
```

### Pre-requisites

In `~/compose/`:
```bash
touch docker-compose.yml && nano docker-compose.yml
```

Stop all running docker containers:
```bash
docker stop serv-madm serv-bdd serv-wordpress serv-nginx
```

### Networks

Adapt the command previously used to create a network:
```bash
docker network create \
--subnet=172.18.10.0/24 \
resTP
```

In `docker-compose.yml` will become:
```yml
version: "3.9"

# services: ...

networks:
  tp.coud:
    ipam:
      config:
        - subnet: 172.22.10.0/24
```

### Nginx

```bash
docker run -d \
--name serv-nginx \
-p 80:80 \
--net=resTP \
--ip=172.18.10.105 \
-v /home/ubuntu/nginx.conf:/etc/nginx/nginx.conf:ro \
-v /home/ubuntu/docker/data/nginx/:/www/ \
nginx:latest
```

```yml
version: "3.8"

services:

  nginx:
    image: nginx:latest
    networks:
      tp.cloud:
        aliases:
          - web.tp.cloud
        ipv4_address: 172.22.10.20
    ports:
      - "80:80"
    volumes:
      # or short syntax: "./Config/nginx/nginx.conf:/etc/nginx/nginx.conf:ro"
      - type: bind
        source: ./Config/nginx/nginx.conf
        target: /etc/nginx/nginx.conf
        read_only: true
    depends_on:
      - myadmin
      - wordpress1
      - wordpress2
    restart: unless-stopped

# networks: ...
```

### MySql

```bash
docker run -d \
--name serv-bdd \
--hostname basededonnee \
-e MYSQL_ROOT_PASSWORD=ppaasswwoorrdd \
-e MYSQL_USER=userwordpress \
-e MYSQL_PASSWORD=passwordpress \
-e MYSQL_DATABASE=wordpress \
-v /home/ubuntu/docker/data/base8/:/var/lib/mysql/ \
--net=resTP \
--ip=172.18.10.100 \
--network-alias=bdd \
mysql:8
```

```yml
version: "3.8"

services:

  # nginx: ...
  
  basededonnees:
    image: mysql:8
    networks:
      tp.cloud:
        aliases:
          - mysql.tp.cloud
          - base.tp.cloud
          - bdd.tp.cloud
    volumes:
      # or short syntax...
      - type: bind
        source: ./Data/mysql/
        target: /var/lib/mysql/
    environment:
      MYSQL_ROOT_PASSWORD: ppaasswwoorrdd
      MYSQL_USER: wp_user
      MYSQL_PASSWORD: wp_pass
      MYSQL_DATABASE: wp_base
    restart: unless-stopped
    healthcheck:
      test: "mysql -uwp_user -pwp_pass"
      interval: 2s
      timeout: 6s
      retries: 40
      start_period: 15s

# networks: ...
```

### phpMyAdmin

```bash
docker run -d \
--name serv-madm \
-e PMA_HOST=bdd \
-e PMA_ABSOLUTE_URI=http://192.168.246.47/pma/ \
--net=resTP \
--ip=172.18.10.101 \
--network-alias=pma.tpcloud \
phpmyadmin/phpmyadmin:latest
```

```yml
version: "3.8"

services:

  # nginx: ...
  # basededonnees: ...
  
  myadmin:
    image: phpmyadmin/phpmyadmin
    networks:
      tp.cloud:
        aliases:
          - phpmyadmin.tp.cloud
          - pma.tp.cloud
    environment:
      PMA_HOST: bdd.tp.cloud
      PMA_ABSOLUTE_URI: http://192.168.246.47/madm/
    depends_on:
      - basededonnees
    restart: unless-stopped

# networks: ...
```

### wordpress1

```yml
version: "3.8"

services:

  # nginx: ...
  # basededonnees: ...
  # myadmin: ...
  
  wordpress1:
    build:
      context: ./Build/wordpress/
    networks:
      tp.cloud:
        aliases:
          - wordpress1.tp.cloud
          - wp1.tp.cloud
    volumes:
      # or short syntax (yml array notation): - "<SRC>:<TARG>:ro" 
      - type: bind
        source: ./Data/php/
        target: /var/www/html/
    environment:
      # using object syntax (or array syntax "- <VAR>=<VALUE>")
      WORDPRESS_DB_HOST: mysql.tp.cloud
      WORDPRESS_DB_USER: wp_user
      WORDPRESS_DB_PASSWORD: wp_pass
      WORDPRESS_DB_NAME: wp_base
    depends_on:
      - basededonnees
    restart: unless-stopped

# networks: ...
```

### wordpress_install

```bash
docker run -it --rm \
--volumes-from serv-wordpress \
--network=resTP \
-e WORDPRESS_DB_HOST=bdd \
-e WORDPRESS_DB_USER=userwordpress \
-e WORDPRESS_DB_PASSWORD=passwordpress \
-e WORDPRESS_DB_NAME=wordpress \
wordpress:cli \
wp core install \
--url=http://192.168.246.47/ \
--title="Mon Site Wordpress" \
--admin_user=lemaitre \
--admin_password=ppaasswwoorrdd \
--admin_email=monmail@univ-lyon1.fr \
--skip-email
```

```yml
version: "3.8"

services:

  # nginx: ...
  # basededonnees: ...
  # myadmin: ...
  # wordpress1: ...

  wordpress_install:
    image: wordpress:cli
    networks:
      - tp.cloud
    volumes_from:
      - wordpress1
    environment:
      # using object syntax (or array syntax "- <VAR>=<VALUE>")
      WORDPRESS_DB_HOST: mysql.tp.cloud
      WORDPRESS_DB_USER: wp_user
      WORDPRESS_DB_PASSWORD: wp_pass
      WORDPRESS_DB_NAME: wp_base
    depends_on:
      wordpress1:
        condition: service_healthy
      basededonnees:
        condition: service_healthy
    restart: "no"
    tty: true
    stdin_open: true
    command: wp core install --url=http://192.168.246.47/ --title="Mon Site Wordpress" --admin_user=monadm --admin_password=monpass --admin_email=monmail@tp.cloud --skip-email

# networks: ...
```

wordpress2
---

```yml
wordpress2:
    build:
      context: ./Build/wordpress/
    depends_on:
      - wordpress1
    volumes:
      # or short syntax (yml array notation): - "<SRC>:<TARG>:ro" 
      - type: bind
        source: ./Data/php/
        target: /var/www/html/
    networks:
      tp.cloud:
        aliases:
          - wordpress2.tp.cloud
          - wp2.tp.cloud
    environment:
      # using object syntax (or array syntax "- <VAR>=<VALUE>")
      WORDPRESS_DB_HOST: mysql.tp.cloud
      WORDPRESS_DB_USER: wp_user
      WORDPRESS_DB_PASSWORD: wp_pass
      WORDPRESS_DB_NAME: wp_base
    restart: unless-stopped
```

### Compose-file

> Modify nginx compose configuration:
>   - change `wordpress` in `depends_on` to `wordpress1` and `wordpress2` 
>   - change `phpmyadmin` in `depends_on` to `myadmin`

> Added `healthcheck` to `basededonnees` service. Also checking if `basededonnees` is `healthy` in the `depends_on` of `wordpress_install` service

> Added `PMA_ABSOLUTE_URI` variable in the environment of `myadmin` service in order to fix a false redirection after logging in to the *phpMyAdmin*

LetsEncrypt
---

### Pre-requisites

#### Sur la plateforme Openstack

1) Create an application account on the OpenStack AND save the OPENRC file
2) Share this OPENRC file with the docker

#### Variables d'environnement pour le container docker

- `CERTBOT_NAME`: grognon
- `CERTBOT_DOMAIN`: cloudtiw.os.univ-lyon1.fr
- `CERTBOT_MAIL`: eldar.kasmamytov@etu.univ-lyon1.fr
- `CERTBOT_IP`: 192.168.246.47

### Commandes

#### Inside the **Image** (`RUN` directive in `Dockerfile`):

##### Install Certbot

```bash
# via Snap
snap install core
snap refresh core
snap install --classic certbot
ln -s /snap/bin/certbot /usr/bin/certbot
```

```bash
# .deb package with APT
apt update
apt -y install certbot
```

##### Install Openstack CLI

**Only if** Ubuntu version below 22, add repo before installing:
```bash
apt -y install software-properties-common
add-apt-repository -y cloud-archive:xena
```

Install:
```bash
apt -y install python3-openstackclient python3-designateclient python3-osc-placement
```

#### Container (`CMD` directive in `Dockerfile`):

```bash
# ========== Source OPENRC ==========
# this file contains authentication credentials
# for the Openstack platform.
# needed to create a DNS record with openstack cli.
source ~/app-cred-my-app-credential-openrc.sh

# ========== Create a DNS record ==========
openstack recordset create $CERTBOT_DOMAIN. --type A $CERTBOT_NAME --records $CERTBOT_IP

# ========== Get script for auth-hook ==========
wget https://documentation.univ-lyon1.fr/downloads/letsencrypt-designate
chmod a+x $(pwd)/letsencrypt-designate

# ========== Generate SSL/TLS Cert ==========
certbot certonly \
--server https://acme-staging-v02.api.letsencrypt.org/directory \
-n -manual-public-ip-logging-ok \
--manual \
--preferred-challenges=dns \
--agree-tos \
--manual-auth-hook $(pwd)/letsencrypt-designate \
-m eldar.kasmamytov@etu.univ-lyon1.fr \
-d demoencrypt.doc.os.univ-lyon1.fr
```

