# Generated by Django 3.0.8 on 2020-07-20 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='register',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=30)),
                ('nmo', models.CharField(max_length=40)),
                ('headname', models.CharField(max_length=20)),
                ('address', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=20)),
                ('phno', models.IntegerField()),
                ('uniqueid', models.IntegerField()),
                ('password', models.CharField(max_length=20)),
            ],
        ),
    ]
