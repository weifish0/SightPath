# Generated by Django 4.2.1 on 2023-11-11 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='artifacts',
            field=models.TextField(blank=True, null=True),
        ),
    ]
