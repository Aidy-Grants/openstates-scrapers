FROM python:3.9-slim
LABEL maintainer="James Turk <dev@jamesturk.net>"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING='utf-8' \
    LANG='C.UTF-8'

RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends \
        gnupg \
        dirmngr \
        ca-certificates \
        curl \
        wget \
        unzip \
        mdbtools \
        libpq5 \
        libgdal32 \
        git \
        libssl-dev \
        libffi-dev \
        freetds-dev \
        libxml2-dev \
        libxslt-dev \
        libyaml-dev \
        poppler-utils \
        libgeos-dev \
        build-essential \
        libpq-dev \
        libgdal-dev \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends gh \
    && pip --no-cache-dir --disable-pip-version-check install wheel crcmod poetry \
    && apt-get remove -y --purge build-essential libpq-dev libgdal-dev \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ADD poetry.lock pyproject.toml /opt/openstates/openstates/
WORKDIR /opt/openstates/openstates/
ENV PYTHONPATH=./scrapers
RUN poetry config virtualenvs.create false \
    && poetry install --no-root

ADD . /opt/openstates/openstates/

# the last step cleans out temporarily downloaded artifacts for poetry, shrinking our build
RUN poetry install \
    && rm -r /root/.cache/pypoetry/cache /root/.cache/pypoetry/artifacts/ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV OPENSSL_CONF=/opt/openstates/openstates/openssl.cnf

COPY entrypoint.sh upload_to_s3.py /opt/openstates/openstates/
RUN chmod +x /opt/openstates/openstates/entrypoint.sh

ENTRYPOINT ["/opt/openstates/openstates/entrypoint.sh"]
