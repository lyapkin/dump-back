import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from urllib.parse import urljoin
from datetime import datetime
from time import time
from django.utils.text import slugify
from unidecode import unidecode
from django.utils.translation import get_language


def slugify_filename(filename):
    filename_split = filename.split(".")
    no_extention_filename = "_".join(filename_split[:-1]).strip("-_")
    extention = filename_split[-1]
    return f"{slugify(unidecode(no_extention_filename))}-{int(time() * 1000)}.{extention}"


class CustomStorage(FileSystemStorage):
    """
    Кастомное расположение для медиа файлов редактора
    """

    def get_folder_name(self):
        return datetime.now().strftime("%Y/%m/%d")

    def get_valid_name(self, name):
        return slugify_filename(name)

    def _save(self, name, content):
        folder_name = self.get_folder_name()
        name = os.path.join(folder_name, self.get_valid_name(name))
        return super()._save(name, content)

    location = os.path.join(settings.MEDIA_ROOT, "uploads")
    base_url = urljoin(settings.MEDIA_URL, "uploads/")


def upload_product_file_to(instance, filename):
    locale = instance.language_code
    new_filename = slugify_filename(filename)
    return f"docs/products/{instance.master.product.id}/{locale}/{new_filename}"


def upload_product_img_to(instance, filename):
    new_filename = slugify_filename(filename)
    return "images/products/{product}/{filename}".format(product=instance.product.slug, filename=new_filename)


def upload_category_img_to(instance, filename):
    new_filename = slugify_filename(filename)
    return "images/categories/{filename}".format(filename=new_filename)


def upload_group_img_to(instance, filename):
    new_filename = slugify_filename(filename)
    return "images/groups/{filename}".format(filename=new_filename)


def generate_unique_slug(klass, field):
    origin_slug = slugify(unidecode(field))
    unique_slug = origin_slug
    numb = 1
    while klass.objects.filter(slug=unique_slug).exists():
        unique_slug = f"{origin_slug}-{numb}"
        numb += 1
    return unique_slug


def generate_unique_slug_translated(klass, klass2, field):
    origin_slug = slugify(unidecode(field))
    unique_slug = origin_slug
    numb = 1
    while klass.objects.filter(translations__slug=unique_slug).exists() or (
        klass2 is not None and klass2.objects.filter(old_slug=unique_slug).exists()
    ):
        unique_slug = f"{origin_slug}-{numb}"
        numb += 1
    return unique_slug


def generate_unique_characteristic_value_slug(klass, field, obj):
    origin_slug = slugify(unidecode(field))
    unique_slug = origin_slug
    numb = 1
    while klass.objects.filter(
        characteristic=obj.characteristic.id,
        translations__slug=unique_slug,
        translations__language_code=obj.language_code,
    ).exists():
        unique_slug = f"{origin_slug}-{numb}"
        numb += 1
    return unique_slug
