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
RUN sudo snap install core
RUN sudo snap refresh core

RUN sudo snap install --classic certbot
RUN sudo ln -s /snap/bin/certbot /usr/bin/certbot

# ========== Install Openstack CLI ==========
RUN sudo apt -y install python3-openstackclient python3-designateclient python3-osc-placement

# ========== Importer le fichier OPENRC ==========
# issue de la craetion d'un compte applicatif sur Openstack
COPY openrc.sh ~/openrc.sh
RUN chmod a+x ~/openrc.sh

# ========== Importer le script de conf ==========
COPY script-docker.sh ~/script-docker.sh
RUN chmod a+x ~/script-docker.sh

# Executer le script
CMD ~/script-docker.sh
