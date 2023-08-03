#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py migrate
# python ./base/fixtures/competitions_fixture_generate.py
# python manage.py flush
python manage.py loaddata ./base/fixtures/tags_fixture.json
python manage.py loaddata ./base/fixtures/competitions_fixture.json
python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate