# Generated by Django 4.2.1 on 2023-10-16 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="bio",
            field=models.CharField(default="", max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="nickname",
            field=models.CharField(
                default="使用者<django.db.models.query_utils.DeferredAttribute object at 0x0000019845C129D0>",
                max_length=20,
            ),
        ),
    ]