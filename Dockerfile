FROM python:3.9

ENV PYTHONUNBUFFERED 1
ENV PYTHONUTF8 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# copy current project directory to container /app
COPY . /app
# change working directory in container
WORKDIR /app

# update pip and tools
RUN pip install --upgrade pip setuptools wheel
# setup path for Poetry
ENV PATH="/root/.local/bin:$PATH"
# don't use virtual environment for poetry
ENV POETRY_VIRTUALENVS_CREATE=false
# download and install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
# setup project dependencies and make poetry.lock file
RUN poetry install --no-interaction --no-ansi

RUN chmod -R +x scripts

CMD ["/app/scripts/run-local.sh"]