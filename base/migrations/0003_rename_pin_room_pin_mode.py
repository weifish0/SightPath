# Generated by Django 4.2.1 on 2023-11-02 03:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0002_room_pin"),
    ]

    operations = [
        migrations.RenameField(model_name="room", old_name="pin", new_name="pin_mode",),
    ]
