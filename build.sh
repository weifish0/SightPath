#!/usr/bin/env bash
# exit on error
set -o errexit

# sudo apt update
# sudo apt install firewalld
# sudo systemctl enable firewalld
# sudo systemctl start firewalld
# sudo firewall-cmd --state
# sudo firewall-cmd --list-all
# sudo firewall-cmd --permanent --add-port=80/tcp
# sudo firewall-cmd --reload

# sudo apt install ttf-mscorefonts-installer 
# sudo apt install latex-cjk-chinese
# sudo apt-get install language-pack-zh*
# sudo apt-get install chinese*


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

