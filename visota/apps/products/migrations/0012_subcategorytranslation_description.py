# Generated by Django 5.0.3 on 2024-09-30 08:01

from django.db import migrations, models


def set_my_defaults(apps, schema_editor):
    SubCategory = apps.get_model("products", "SubCategory")
    SubCategoryTranslation = apps.get_model('products', 'SubCategoryTranslation')
    for cat in SubCategory.objects.all():
        translations = SubCategoryTranslation.objects.filter(master_id=cat.id)
        for translation in translations:
            translation.description = translation.name
            translation.save()

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_alter_categoryredirectfrom_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcategorytranslation',
            name='description',
            field=models.TextField(null=True, verbose_name='описание'),
        ),
        migrations.RunPython(set_my_defaults, None),
        migrations.AlterField(
            model_name='subcategorytranslation',
            name='description',
            field=models.TextField(verbose_name='описание'),
        ),
    ]
