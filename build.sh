#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate

#########
# python ./base/fixtures/competitions_fixture_generator.py
python3 manage.py loaddata ./base/fixtures/competition_tags_fixture.json
python3 manage.py loaddata ./base/fixtures/competitions_fixture.json
python3 manage.py loaddata ./base/fixtures/ourtag_fixture.json
# python manage.py loaddata ./base/fixtures/activities_fixture.json
#########

python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate