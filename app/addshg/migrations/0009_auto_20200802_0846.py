# Generated by Django 3.0.1 on 2020-08-02 03:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addshg', '0008_auto_20200802_0814'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loan',
            name='Score',
        ),
        migrations.AddField(
            model_name='loanregister',
            name='Score',
            field=models.IntegerField(default=10),
        ),
    ]