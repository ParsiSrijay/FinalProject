# Generated by Django 3.0.1 on 2020-07-27 13:04

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_ledger_regimo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Shgloans', models.IntegerField()),
                ('Feesandcharges', models.IntegerField()),
                ('Salaries', models.IntegerField()),
                ('Adminexpenses', models.IntegerField()),
                ('Stationery', models.IntegerField()),
                ('Micellaneous', models.IntegerField()),
                ('Closingbal', models.IntegerField()),
                ('RegIMO', models.CharField(default='', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Receipts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Date', models.DateField(default=django.utils.timezone.now)),
                ('Memfees', models.IntegerField()),
                ('Fines', models.IntegerField()),
                ('Interests', models.IntegerField()),
                ('Principal', models.IntegerField()),
                ('Openingbal', models.IntegerField()),
                ('Rmkfunds', models.IntegerField()),
                ('RegIMO', models.CharField(default='', max_length=10)),
            ],
        ),
    ]
