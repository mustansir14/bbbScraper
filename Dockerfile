FROM python:3.11.1-bullseye

WORKDIR /www

RUN apt-get update
RUN pip3 install --upgrade pip
RUN apt install -y wget curl gpg

RUN wget https://r.mariadb.com/downloads/mariadb_repo_setup
RUN chmod +x mariadb_repo_setup
RUN ./mariadb_repo_setup --mariadb-server-version="mariadb-10.9"

RUN apt install -y libmariadb3 libmariadb-dev
RUN apt install -y xvfb

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

#RUN apt-get install chromium-browser

COPY ./install/requirements.txt ./install/requirements.txt
RUN pip3 install -r ./install/requirements.txt

COPY . /www

CMD python "${APP_TARGET}" --no_of_threads ${APP_NO_OF_THREADS}