# HAPI stress testing

## Setup

### Docker

Download the PostgreSQL docker image:

```shell
docker pull postgres
```

Start the container:

```shell
docker compose up -d
```

Note that the database username and password are hard-coded directly in
the docker-compose file, as it's only meant for testing. Also, the
database will be mounted to `$HOME/postgres_data`.

### Python

Using Python 3.11, install the requirements:

```shell
pip install -r requirements.txt
```

### Database

Populate the database:

```shell
python main.py
```

Create other tables:
```shell
cat table_scripts/create_multi_tables.sql \
    | docker exec -i hapi-stress-test-db \
    psql -h localhost -U postgres -d hapi
```

## Exploration

To enter the database:

```shell
docker exec -it hapi-stress-test-db psql -U postgres -d hapi
````

## Stress tests

The stress tests involve a timed query. Run:

```shell
cd test_scripts
timed_query.sh 01_standard_query.sql
timed_query.sh 02_filter_date.sql
timed_query.sh 03_pivot.sql
timed_query.sh 04_join.sql
```

## Development

Be sure to install `pre-commit`, which is run every time
you make a git commit:

```shell
pip install pre-commit
pre-commit install
```

The configuration file for this project is in a
non-start location. Thus, you will need to edit your
`.git/hooks/pre-commit` file to reflect this. Change
the first line that begins with `ARGS` to:

```shell
ARGS=(hook-impl --config=.config/pre-commit-config.yaml --hook-type=pre-commit)
```

With pre-commit, all code is formatted according to
[black]("https://github.com/psf/black") and
[ruff]("https://github.com/charliermarsh/ruff") guidelines.

To check if your changes pass pre-commit without committing, run:

```shell
pre-commit run --all-files --config=.config/pre-commit-config.yaml
```
