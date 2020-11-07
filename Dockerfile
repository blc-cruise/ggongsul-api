FROM python:3.9 as builder
# Install Poetgry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./

ARG APP_ENV=development
ENV PYTHONUNBUFFERED=1 APP_ENV=${APP_ENV}

RUN bash -c "if [ ${APP_ENV} == 'development' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

FROM python:3.9-slim as prod

LABEL maintainer="jaegeon <zezaeoh@gmail.com>"

RUN ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime
RUN chmod 777 /tmp
RUN apt-get update && apt-get install -y --no-install-recommends \
        locales rdate openssl ca-certificates \
    && localedef -f UTF-8 -i ko_KR ko_KR.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

ARG APP_ENV=development
ENV LANG="ko_KR.UTF-8" LANGUAGE="ko_KR.UTF-8" LC_ALL="ko_KR.UTF-8" \
    PYTHONUNBUFFERED=1 APP_ENV=${APP_ENV} \
    UWSGI_PORT="8000" UWSGI_THREAD_NUM="2" UWSGI_PROCESS_NUM="2" UWSGI_LISTEN_NUM="1024"

WORKDIR /app

COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

COPY . .

ENTRYPOINT ["/app/bin/docker-entrypoint"]
