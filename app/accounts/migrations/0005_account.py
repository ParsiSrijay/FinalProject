# Generated by Django 3.0.1 on 2020-08-01 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_receipts_micellaneous'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Field', models.CharField(max_length=15)),
                ('RandP', models.CharField(max_length=10)),
                ('IandE', models.CharField(max_length=10)),
                ('BalSheet', models.CharField(max_length=10)),
                ('Amount', models.IntegerField(default=0)),
            ],
        ),
    ]
