FROM python:3.11.4-slim-bullseye

ARG RSS_FEED_TOOLBOX_VERSION

LABEL authors="qhuang"

ENV LANG="C.UTF-8" \
    TZ="Asia/Shanghai" \
    HOME="/rssfeedtoolbox" \
    CONFIG_DIR="/config" \
    TERM="xterm" \
    PUID=0 \
    PGID=0 \
    UMASK=000 \

WORKDIR /app

RUN apt-get update -y && apt-get -y install nginx locales gosu gcc git curl busybox && \
    rm -rf \
        /tmp/* \
        /rssfeedtoolbox/.cache \
        /var/lib/apt/lists/* \
        /var/tmp/*

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt \
    && rm -rf \
        /tmp/* \
        /rssfeedtoolbox/.cache \
        /var/lib/apt/lists/* \
        /var/tmp/*

COPY . .

RUN cp -f /app/nginx.conf /etc/nginx/nginx.conf \
    && cp -f /app/entrypoint /entrypoint \
    && chmod +x /entrypoint \
    && groupadd -r rssfeedtoolbox -g 911 \
    && useradd -r rssfeedtoolbox -g rssfeedtoolbox -d ${HOME} -s /bin/bash -u 911 \
    && locale-gen zh_CN.UTF-8 \
    && FRONTEND_VERSION=$(curl -sL "https://api.github.com/repos/yellowstrong/Frontend/releases/latest" | jq -r .tag_name) \
    && curl -sL "https://github.com/yellowstrong/Frontend/releases/download/${FRONTEND_VERSION}/dist.zip" | busybox unzip -d / - \
    && mv /dist /frontend

EXPOSE 3030
VOLUME [ "/config" ]
ENTRYPOINT [ "/entrypoint" ]