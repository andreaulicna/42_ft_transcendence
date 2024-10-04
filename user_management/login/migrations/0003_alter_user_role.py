# Generated by Django 5.1.1 on 2024-10-04 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_alter_user_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('player', 'Player')], default='player', max_length=15),
        ),
    ]
