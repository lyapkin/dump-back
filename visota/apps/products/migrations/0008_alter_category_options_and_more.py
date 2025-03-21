# Generated by Django 5.0.3 on 2024-09-22 19:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_alter_producttranslation_slug_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'группа категории', 'verbose_name_plural': 'группы категорий'},
        ),
        migrations.AlterModelOptions(
            name='categorytranslation',
            options={'default_permissions': (), 'managed': True, 'verbose_name': 'группа категории Translation'},
        ),
        migrations.AlterModelOptions(
            name='subcategory',
            options={'verbose_name': 'категория', 'verbose_name_plural': 'категории'},
        ),
        migrations.AlterModelOptions(
            name='subcategorytranslation',
            options={'default_permissions': (), 'managed': True, 'verbose_name': 'категория Translation'},
        ),
        migrations.AlterField(
            model_name='categorytranslation',
            name='name',
            field=models.CharField(max_length=50, unique=True, verbose_name='название группы'),
        ),
        migrations.AlterField(
            model_name='product',
            name='sub_categories',
            field=models.ManyToManyField(related_name='products', to='products.subcategory', verbose_name='категория товара'),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='products.category', verbose_name='группа'),
        ),
        migrations.AlterField(
            model_name='subcategorytranslation',
            name='name',
            field=models.CharField(max_length=50, unique=True, verbose_name='название категории'),
        ),
    ]
