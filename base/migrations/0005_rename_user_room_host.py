# Generated by Django 4.2.1 on 2023-06-05 10:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0004_room_user"),
    ]

    operations = [
        migrations.RenameField(model_name="room", old_name="user", new_name="host",),
    ]
