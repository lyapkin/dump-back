# Generated by Django 5.0.3 on 2024-10-01 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seo', '0016_cssfile_jsfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cssfile',
            name='content',
            field=models.TextField(blank=True, null=True, verbose_name='код'),
        ),
        migrations.AlterField(
            model_name='jsfile',
            name='content',
            field=models.TextField(blank=True, null=True, verbose_name='код'),
        ),
    ]
