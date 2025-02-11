# Generated by Django 5.1.1 on 2025-01-22 12:05

import api.models
import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.postgres.fields
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('player', 'Player')], default='player', max_length=15)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('win_count', models.PositiveIntegerField(default=0)),
                ('loss_count', models.PositiveIntegerField(default=0)),
                ('state', models.CharField(choices=[('ID', 'Idle'), ('IG', 'In game')], default='ID', max_length=3)),
                ('status_counter', models.PositiveIntegerField(default=0)),
                ('avatar', models.ImageField(blank=True, upload_to=api.models.user_directory_path)),
                ('two_factor', models.BooleanField(default=False)),
                ('two_factor_secret', models.CharField(blank=True, max_length=32, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AIMatch',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('WAIT', 'Waiting'), ('IP', 'In progress'), ('FIN', 'Finished')], default='WAIT', max_length=4)),
                ('player1_score', models.PositiveIntegerField(default=0)),
                ('player2_score', models.PositiveIntegerField(default=0)),
                ('default_ball_size', models.FloatField(default=0)),
                ('default_paddle_height', models.FloatField(default=0)),
                ('default_paddle_width', models.FloatField(default=0)),
                ('default_paddle_speed', models.FloatField(default=0)),
                ('round_number', models.PositiveIntegerField(default=0)),
                ('winner', models.CharField(blank=True, max_length=150)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ai_creator', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('PEN', 'Pending'), ('ACC', 'Accepted')], default='PEN', max_length=3)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LocalTournament',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='unnamed', max_length=30)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('WAIT', 'Waiting'), ('IP', 'In progress'), ('FIN', 'Finished')], default='WAIT', max_length=4)),
                ('capacity', models.PositiveIntegerField(default=0)),
                ('winner', models.CharField(blank=True, max_length=150)),
                ('players', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=150), blank=True, default=list, size=None)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_creator', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LocalMatch',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('WAIT', 'Waiting'), ('IP', 'In progress'), ('FIN', 'Finished')], default='WAIT', max_length=4)),
                ('player1_score', models.PositiveIntegerField(default=0)),
                ('player2_score', models.PositiveIntegerField(default=0)),
                ('default_ball_size', models.FloatField(default=0)),
                ('default_paddle_height', models.FloatField(default=0)),
                ('default_paddle_width', models.FloatField(default=0)),
                ('default_paddle_speed', models.FloatField(default=0)),
                ('round_number', models.PositiveIntegerField(default=0)),
                ('player1_tmp_username', models.CharField(blank=True, max_length=150)),
                ('player2_tmp_username', models.CharField(blank=True, max_length=150)),
                ('winner', models.CharField(blank=True, max_length=150)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='local_creator', to=settings.AUTH_USER_MODEL)),
                ('tournament', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.localtournament')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='unnamed', max_length=30)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('WAIT', 'Waiting'), ('IP', 'In progress'), ('FIN', 'Finished')], default='WAIT', max_length=4)),
                ('capacity', models.PositiveIntegerField(default=0)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_creator', to=settings.AUTH_USER_MODEL)),
                ('winner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='winner_tournament', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PlayerTournament',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('player_tmp_username', models.CharField(blank=True, max_length=150)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.tournament')),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('WAIT', 'Waiting'), ('IP', 'In progress'), ('FIN', 'Finished')], default='WAIT', max_length=4)),
                ('player1_score', models.PositiveIntegerField(default=0)),
                ('player2_score', models.PositiveIntegerField(default=0)),
                ('default_ball_size', models.FloatField(default=0)),
                ('default_paddle_height', models.FloatField(default=0)),
                ('default_paddle_width', models.FloatField(default=0)),
                ('default_paddle_speed', models.FloatField(default=0)),
                ('round_number', models.PositiveIntegerField(default=0)),
                ('player1', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='player1', to=settings.AUTH_USER_MODEL)),
                ('player2', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='player2', to=settings.AUTH_USER_MODEL)),
                ('winner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='winner_match', to=settings.AUTH_USER_MODEL)),
                ('tournament', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.tournament')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
