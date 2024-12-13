# Generated by Django 5.1.1 on 2024-12-13 12:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_remove_match_match_type_and_more'),
    ]

    operations = [
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
                ('winner', models.CharField(blank=True, max_length=150)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ai_creator', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
