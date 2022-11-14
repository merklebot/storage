FROM python:3.10.6 as requirements-stage
WORKDIR /tmp
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN wget -q https://dist.ipfs.tech/kubo/v0.16.0/kubo_v0.16.0_linux-amd64.tar.gz && \
    tar -xvzf kubo_v0.16.0_linux-amd64.tar.gz

FROM python:3.10.6
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY --from=requirements-stage /tmp/kubo/ipfs /usr/local/bin
RUN ipfs init
WORKDIR /storage
COPY --from=requirements-stage /tmp/requirements.txt /storage/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /storage/requirements.txt
COPY . /storage/
