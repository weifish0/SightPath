# Generated by Django 4.2.1 on 2023-10-16 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0004_alter_user_id_alter_user_nickname"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="nickname",
            field=models.CharField(default="", max_length=20),
        ),
    ]