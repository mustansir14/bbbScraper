FROM python:3.13-rc-bookworm

ARG UID
ARG GID

RUN addgroup --gid $GID nonroot && \
    adduser --uid $UID --gid $GID --disabled-password --gecos "" nonroot && \
    echo 'nonroot ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

RUN apt-get update && \
    pip3 install --upgrade pip && \
    apt install -y wget curl gpg iotop xvfb lsof libmariadb3 libmariadb-dev && \
    ldconfig gpg

ENV CHROME_VERSION=119.0.6045.105-1
RUN wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb && \
    apt install -y ./google-chrome-stable_${CHROME_VERSION}_amd64.deb

RUN wget https://r.mariadb.com/downloads/mariadb_repo_setup && \
    chmod +x mariadb_repo_setup && \
    ./mariadb_repo_setup
#    ./mariadb_repo_setup --mariadb-server-version="mariadb-10.9"

# chrome version + "-1"


USER nonroot
WORKDIR /www

COPY --chown=nonroot:nonroot ./install/requirements.txt ./install/requirements.txt
RUN pip3 install -r ./install/requirements.txt

COPY --chown=nonroot:nonroot . /www