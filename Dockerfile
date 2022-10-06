FROM python:3.10.6 as requirements-stage
WORKDIR /tmp
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.10.6
WORKDIR /storage
COPY --from=requirements-stage /tmp/requirements.txt /storage/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /storage/requirements.txt
COPY storage /storage/storage
CMD ["python", "-m", "storage"]
