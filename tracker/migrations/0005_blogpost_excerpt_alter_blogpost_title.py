# Generated by Django 4.2.19 on 2025-04-29 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0004_blogpost'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='excerpt',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='blogpost',
            name='title',
            field=models.CharField(max_length=200),
        ),
    ]
