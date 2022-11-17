FROM ubuntu:22.04


# addaptation à la situation d'une VM openstack de l'université
# pour apt
RUN echo 'Acquire::http::Proxy "http://proxy.univ-lyon1.fr:3128";' > /etc/apt/apt.conf.d/99proxy
# var d'env
ENV DEBIAN_FRONTEND=noninteractiv
ENV HTTP_PROXY=http://proxy.univ-lyon1.fr:3128
ENV HTTPS_PROXY=http://proxy.univ-lyon1.fr:3128
ENV ALL_PROXY=http://proxy.univ-lyon1.fr:3128
ENV http_proxy=http://proxy.univ-lyon1.fr:3128
ENV https_proxy=http://proxy.univ-lyon1.fr:3128
ENV all_proxy=http://proxy.univ-lyon1.fr:3128
ENV NO_PROXY=.univ-lyon1.fr
ENV no_proxy=.univ-lyon1.fr

# ------------------------------------------------------------------------------
# exemple d'installation d'un utilitaire
# ------------------------------------------------------------------------------

# Attention, c'est généralement une mauvaise idée d'installe ce type d'utilitaire dans un docker. En effet, curl permet de télécharger tout et n'importe quoi.
# cela signifie qu'un attanquant qui s'introduit dans le docker peut facilement récupérer des outils pour allez plus loin. C'est utilisé ici uniquement pour
# les besoins du script de test
RUN apt-get update && apt-get -y install net-tools inetutils-ping inetutils-telnet netcat-openbsd curl && apt-get clean

RUN apt-get update && apt-get -y install python3-openstackclient python3-designateclient python3-osc-placement && apt-get clean

RUN apt-get update && apt-get -y install certbot && apt-get clean


# ------------------------------------------------------------------------------
# MY CODE
# ------------------------------------------------------------------------------

# ========== Install Certbot ==========
RUN apt update
RUN apt install -y certbot

# ========== Install Openstack CLI ==========
RUN apt -y install python3-openstackclient python3-designateclient python3-osc-placement

# ========== Importer le fichier OPENRC ==========
# issue de la craetion d'un compte applicatif sur Openstack
COPY openrc.sh /usr/local/bin/openrc.sh
RUN chmod a+x /usr/local/bin/openrc.sh

# ========== Importer le script de conf ==========
COPY script-docker.sh /usr/local/bin/script-docker.sh
RUN chmod a+x /usr/local/bin/script-docker.sh

# ========== Importer le script designate ==========
COPY letsencrypt-designate /usr/local/bin/letsencrypt-designate
RUN chmod a+x /usr/local/bin/letsencrypt-designate

#HEALTHCHECK --interval=1s --timeout=3s --retries=60 --start-period=5s \
#  CMD "test -f /etc/letsencrypt/live/grognon.cloudtiw.os.univ-lyon1.fr/fullchain.pem && test -f /etc/letsencrypt/live/grognon.cloudtiw.os.univ-lyon1.fr/privkey.pem"

# Executer le script
CMD /usr/local/bin/script-docker.sh
