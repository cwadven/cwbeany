# Generated by Django 3.2.12 on 2023-04-08 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatgpt', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='body',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='summary',
            field=models.TextField(blank=True, null=True),
        ),
    ]