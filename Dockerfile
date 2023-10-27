FROM python:3.8-slim-buster AS base

WORKDIR /root
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
# Needed to that flyte can run workflows in the container
ENV PYTHONPATH /root
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100
ENV POETRY_VERSION=1.6.1

RUN apt-get update && apt-get install -y build-essential curl unzip

# System deps:
RUN pip install poetry==$POETRY_VERSION && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -r ./awscliv2.zip ./aws/install

FROM base AS poetry-env

COPY pyproject.toml poetry.lock README.md /root/
# Get secrets from env vars to access private PyPI
RUN --mount=type=secret,id=AWS_ACCESS_KEY_ID \
    --mount=type=secret,id=AWS_SECRET_ACCESS_KEY \
    --mount=type=secret,id=AWS_SESSION_TOKEN \
    --mount=type=secret,id=AWS_DEFAULT_REGION \
    export AWS_ACCESS_KEY_ID=$(cat /run/secrets/AWS_ACCESS_KEY_ID) && \
    export AWS_SECRET_ACCESS_KEY=$(cat /run/secrets/AWS_SECRET_ACCESS_KEY) && \
    export AWS_SESSION_TOKEN=$(cat /run/secrets/AWS_SESSION_TOKEN) && \
    export AWS_DEFAULT_REGION=$(cat /run/secrets/AWS_DEFAULT_REGION) && \
    poetry config virtualenvs.create false  && \
    poetry config installer.max-workers 10 && \
    poetry config http-basic.artifact aws `aws codeartifact get-authorization-token --domain <PRIVATE AWS DOMAIN>  --query authorizationToken --output text` && \
    poetry install --no-interaction --no-ansi --no-root --without dev

FROM poetry-env AS lib-build
# Copy the actual code
COPY src/ /root/src/

RUN poetry install --no-interaction --no-ansi --only-root


FROM lib-build AS runtime

ARG tag
ENV FLYTE_INTERNAL_IMAGE $tag
