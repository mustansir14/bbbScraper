FROM php:7.4-cli

WORKDIR /www

RUN apt-get update
RUN apt-get install -y libzip-dev cron rsyslog vim procps
RUN docker-php-ext-install zip mysqli pdo pdo_mysql

COPY composer.* .

RUN php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"
ENV COMPOSER_ALLOW_SUPERUSER=1
RUN php composer-setup.php
RUN php -r "unlink('composer-setup.php');"
RUN php composer.phar install

# rsyslog setup
RUN echo "*.* /www/logs/cron.log" > /etc/rsyslog.d/console.conf

# crontab for test
#RUN echo "* * * * * root /usr/local/bin/php -r 'echo date(\"c\");' > /www/logs/test.log" > /etc/cron.d/test
#RUN chmod 0644 /etc/cron.d/test

# crontab for export
# BugFix: write username
# BugFix: write full php path
COPY ./.env ./cron.env
RUN echo "0 1 * * * root export \$(cat /www/cron.env | xargs); /usr/local/bin/php /www/export-to-scampulse.php >> /www/logs/export-to-scampulse.errors.log 2>&1" > /etc/cron.d/bbb_scamtracker_export
RUN chmod 0644 /etc/cron.d/bbb_scamtracker_export

COPY . .

RUN ./vendor/bin/phinx migrate

CMD rsyslogd && cron -L 15 && php main.php