#!/usr/bin/env bash

python -m storage --pre-start

alembic upgrade head

python -m storage
