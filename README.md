# EZ Statup Auth Server
We run this application as Authentication server to allow user access to our ecosystem.

## Requirements
1. Django==5.0.7
2. psycopg
3. djangorestframework
4. markdown
5. django-filter
6. django-oauth-toolkit

## Installation
Create Python virtual environment and install requirements.
```bash
python -m venv .venv
source .venv/bin/activate
```	

Install requirements
```bash
pip install -r requirements.txt
```
## Run server on port 8000

```bash
python manage.py runserver 0.0.0.0:8000
```

## Credits & License
