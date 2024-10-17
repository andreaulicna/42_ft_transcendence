# Generated by Django 5.1.1 on 2024-10-15 07:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('round', models.IntegerField(default=1)),
                ('state', models.CharField(choices=[('PLY', 'PLAYED'), ('UPL', 'UNPLAYED')], default='UPL', max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=20)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PlayerMatch',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('score', models.IntegerField(default=0)),
                ('won', models.BooleanField(default=False)),
                ('match_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pong_app.match')),
                ('player_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pong_app.player')),
            ],
        ),
    ]
