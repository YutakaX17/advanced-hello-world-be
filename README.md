# Advanced Hello World Backend

Deployable Django assembler for Advanced Hello World. It supplies project
settings, URL assembly, PostgreSQL configuration, CORS, WSGI/ASGI entry points,
migration commands, module installation, and the production container. Shared
contracts and feature behavior come from separately versioned packages.

`modules.json` is the authoritative, schema-validated record of packages
selected by this assembler. It pins every repository to a full commit SHA and
drives installation, Django application registration, URL registration,
installed-version checks, and feature-contract validation.

## Requirements

- Git
- Python 3.12 or newer
- PostgreSQL 17 for application development
- Docker Engine with Compose for container workflows

## Native setup without Docker

Clone the backend repositories as siblings:

```bash
git clone https://github.com/YutakaX17/advanced-hello-world-be-core.git
git clone https://github.com/YutakaX17/advanced-hello-world-be-messages.git
git clone https://github.com/YutakaX17/advanced-hello-world-be.git
cd advanced-hello-world-be
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python -m advanced_hello_world.module_installer modules.json --local-root ..
```

Omit `--local-root ..` to install the immutable Git commits recorded in the
manifest instead of editable sibling checkouts.

Create a PostgreSQL database and role using your preferred administration tool:

```sql
CREATE ROLE advanced_hello_world LOGIN PASSWORD 'local-development-password';
CREATE DATABASE advanced_hello_world OWNER advanced_hello_world;
```

Create the local development environment file:

```bash
cp .env.example .env
```

Edit `.env` so its database role and password match PostgreSQL. Development
commands launched through `manage.py` load this file automatically. Variables
already exported by the shell take precedence over values in `.env`.

Run migrations and start Django:

```bash
python manage.py migrate
python manage.py runserver
```

Verify the API:

```bash
curl http://localhost:8000/api/v1/health/live
curl -X POST http://localhost:8000/api/v1/messages \
  -H 'Content-Type: application/json' \
  -d '{"text":"Hello from Django"}'
```

## Hybrid setup: PostgreSQL in Docker

If Python should run natively but PostgreSQL should run in a container:

```bash
docker run --name advanced-hello-world-db \
  -e POSTGRES_DB=advanced_hello_world \
  -e POSTGRES_USER=advanced_hello_world \
  -e POSTGRES_PASSWORD=local-development-password \
  -p 5432:5432 \
  -v advanced-hello-world-db:/var/lib/postgresql/data \
  -d postgres:17.5-alpine
```

Set the password in `.env` to the same value used by the container, then use the
native Django commands above. Stop and restart the database with:

```bash
docker stop advanced-hello-world-db
docker start advanced-hello-world-db
```

## Docker setup

Build this service directly. The image installs the exact packages selected by
`modules.json`:

```bash
docker build -t advanced-hello-world-be:local .
```

The image expects PostgreSQL and runtime environment variables, so the
recommended complete setup is the
[distribution repository](https://github.com/YutakaX17/advanced-hello-world):

```bash
git clone https://github.com/YutakaX17/advanced-hello-world.git
cd advanced-hello-world
cp .env.example .env
docker compose up -d --wait
```

## Development and verification

```bash
ruff format --check .
ruff check .
python -m advanced_hello_world.module_manifest modules.json --check-installed
pytest
python manage.py makemigrations --check --dry-run
python manage.py check
```

The test settings use SQLite for fast assembly tests. Local application use and
the distribution use PostgreSQL.

## Production and releases

The container runs as a non-root user and exposes port `8000`. Its health check
uses `/api/v1/health/live`. Released images are published at
`ghcr.io/yutakax17/advanced-hello-world-be` with immutable version tags, image
provenance, and SBOM attestations. A successful version-tag build also creates
a GitHub Release with immutable image metadata, an SPDX image SBOM, and SHA-256
checksums.

Pull requests run backend quality checks, dependency review, CodeQL, secret
scanning, and vulnerability scanning. See [CONTRIBUTING.md](CONTRIBUTING.md),
[SECURITY.md](SECURITY.md), and the
[releases](https://github.com/YutakaX17/advanced-hello-world-be/releases).

## Repository family

- [Backend core](https://github.com/YutakaX17/advanced-hello-world-be-core)
- [Backend messages](https://github.com/YutakaX17/advanced-hello-world-be-messages)
- [Frontend core](https://github.com/YutakaX17/advanced-hello-world-fe-core)
- [Frontend assembler](https://github.com/YutakaX17/advanced-hello-world-fe)
- [All-in-one distribution](https://github.com/YutakaX17/advanced-hello-world)
