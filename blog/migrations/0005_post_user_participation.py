# Generated by Django 4.1.7 on 2023-05-15 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_post_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='user_participation',
            field=models.IntegerField(default=0),
        ),
    ]
