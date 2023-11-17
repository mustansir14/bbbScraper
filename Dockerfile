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

# chrome version + "-1"
ENV CHROME_VERSION=119.0.6045.105-1
RUN wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb
RUN apt install -y ./google-chrome-stable_${CHROME_VERSION}_amd64.deb

COPY ./install/requirements.txt ./install/requirements.txt
RUN pip3 install -r ./install/requirements.txt

COPY . /www

CMD python "${APP_TARGET}" --no_of_threads ${APP_NO_OF_THREADS}