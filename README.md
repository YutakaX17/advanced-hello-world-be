# Advanced Hello World Backend

Deployable Django assembler for Advanced Hello World. The reusable model and API
are supplied by the separately versioned `advanced-hello-world-be-core` package.

## Local development

Clone the backend core beside this repository, then run:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ../advanced-hello-world-be-core
python -m pip install -e '.[dev]'
python manage.py migrate
python manage.py runserver
```

