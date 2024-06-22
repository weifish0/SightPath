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
# sudo firewall-cmd --permanent --add-port=443/tcp
# sudo firewall-cmd --reload

# sudo apt install nginx-extras
# sudo sed -i 's/user www-data/user ubuntu/g' /etc/nginx/nginx.conf

cd ~/SightPath
pip install -r requirements.txt

python3 manage.py makemigrations
python3 manage.py migrate

#########
python3 ./base/fixtures/competitions_fixture_generator.py
python3 ./base/fixtures/activities_fixture_generator.py

python3 ./base/ml/run_label_ourtag.py
python3 ./base/ml/run_label_comp.py
python3 ./base/ml/run_label_activities.py
#########

# python3 manage.py loaddata ./base/fixtures/competition_tags_fixture.json
python3 manage.py syncdata ./base/fixtures/competition_tags_fixture.json
python3 manage.py syncdata ./base/fixtures/competitions_fixture.json
python3 manage.py syncdata ./base/fixtures/ourtag_fixture.json

python3 manage.py syncdata ./base/fixtures/activities_tags_fixture.json
python3 manage.py syncdata ./base/fixtures/activities_fixture.json

# pgrep gunicorn
# pgrep nginx

cd ~/SightPath
git pull
sudo pkill -f gunicorn

sudo cp -f sightpath.conf /etc/nginx/sites-available
sudo ln -nsf /etc/nginx/sites-available/sightpath.conf /etc/nginx/sites-enabled
sudo nohup gunicorn sightpath.wsgi:application > nohup.txt 2>&1 &

sudo systemctl restart nginx


# python manage.py collectstatic --no-input

# sudo pkill -f runserver
# python manage.py runserver 0.0.0.0:80 --insecure
# sudo nohup python3 manage.py runserver 0.0.0.0:80 --insecure

### sudo chown -R www-data:www-data /home/ubuntu/Eosphorus/static/