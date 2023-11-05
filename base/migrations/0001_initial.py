# Generated by Django 4.2.1 on 2023-11-05 22:51

import base.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('bio', models.CharField(blank=True, default='', max_length=150, null=True)),
                ('nickname', models.CharField(max_length=20, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('avatar', models.ImageField(default='avatar.png', null=True, upload_to='')),
                ('is_staff', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_superuser', models.BooleanField(default=False)),
                ('persona', models.ImageField(default='loading.gif', storage=base.models.OverwriteStorage(), upload_to='persona')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
            managers=[
                ('objects', base.models.CustomUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ActivityMainTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='CompetitionTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='OurTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=400)),
                ('emb', models.CharField(max_length=800, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('pin_mode', models.BooleanField(default=False)),
                ('host', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('participants', models.ManyToManyField(blank=True, related_name='participants', to=settings.AUTH_USER_MODEL)),
                ('topic', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.topic')),
            ],
            options={
                'ordering': ['-updated', '-created'],
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.room')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('url', models.URLField(null=True)),
                ('cover_img_url', models.URLField(null=True)),
                ('start_time', models.DateTimeField(null=True)),
                ('end_time', models.DateTimeField(null=True)),
                ('guide_line_html', models.TextField(null=True)),
                ('organizer_title', models.TextField(null=True)),
                ('page_views', models.IntegerField(null=True)),
                ('contact_email', models.EmailField(max_length=254, null=True)),
                ('contact_name', models.TextField(null=True)),
                ('contact_phone', models.TextField(null=True)),
                ('limit_highschool', models.BooleanField(null=True)),
                ('limit_none', models.BooleanField(null=True)),
                ('limit_other', models.BooleanField(null=True)),
                ('emb', models.CharField(max_length=800, null=True)),
                ('our_tags', models.ManyToManyField(blank=True, to='base.ourtag')),
                ('tags', models.ManyToManyField(blank=True, to='base.competitiontag')),
            ],
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('eventIdNumber', models.TextField(null=True)),
                ('start_time', models.DateTimeField(null=True)),
                ('end_time', models.DateTimeField(null=True)),
                ('eventPlaceType', models.TextField(null=True)),
                ('location', models.TextField(null=True)),
                ('likeCount', models.IntegerField(null=True)),
                ('pageView', models.IntegerField(null=True)),
                ('isAD', models.BooleanField(null=True)),
                ('photoUrl', models.URLField(null=True)),
                ('mainTag', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.activitymaintag')),
            ],
        ),
    ]
