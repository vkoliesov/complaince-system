#!/bin/bash

set -o errexit
set -o nounset

# alembic upgrade head
uvicorn main:app --host 0.0.0.0 --log-level info --reload
