FROM wordpress


# addaptation à la situation d'une VM openstack de l'université
# pour apt
RUN echo 'Acquire::http::Proxy "http://proxy.univ-lyon1.fr:3128";' > /etc/apt/apt.conf.d/99proxy
# pour pear et pecl
RUN pear config-set http_proxy http://proxy.univ-lyon1.fr:3128
# pour wordpress
RUN echo "define('WP_PROXY_HOST', 'proxy.univ-lyon1.fr'); define('WP_PROXY_PORT', '3128'); define('WP_PROXY_USERNAME', ''); define('WP_PROXY_PASSWORD', ''); define('WP_PROXY_BYPASS_HOSTS', 'localhost');" >> /usr/src/wordpress/wp-config-docker.php

# -----------------------------------------------------------------------------------
# exemple d'installation d'un utilitaire
# -----------------------------------------------------------------------------------

# Attention, c'est généralement une mauvaise idée d'installe ce type d'utilitaire dans un docker. En effet, curl permet de télécharger tout et n'importe quoi.
# cela signifie qu'un attanquant qui s'introduit dans le docker peut facilement récupérer des outils pour allez plus loin. C'est utilisé ici uniquement pour
# les besoins du script de test
RUN  apt-get update && apt-get -y install net-tools inetutils-ping inetutils-telnet netcat-openbsd curl && apt-get clean
# même remarque sur le fait de créer une page proposant phpinfo et donc donnant beaucoup d'information sur le serveur utilisé.
RUN echo "<?php phpinfo();" > /usr/src/wordpress/serv-infos.php

HEALTHCHECK CMD curl --fail http://localhost:80/ || exit 1

# installation du module redis de php (voir documentation des docker php)
RUN pecl install redis-5.1.1 \
	&& pecl install xdebug-2.8.1 \
	&& docker-php-ext-enable redis xdebug




