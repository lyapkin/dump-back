from django.db import models

from django_ckeditor_5.fields import CKEditor5Field

from common.utils import CustomStorage

# Create your models here.
class Project(models.Model):
    title = models.CharField('название проекта', max_length=100, unique=True)
    slug = models.SlugField("url", max_length=100, unique=True)
    preview_image = models.ImageField("изображение, превью", storage=CustomStorage)
    content = CKEditor5Field("текст статьи", config_name='extends')
    content_concise = models.TextField('краткое описание проекта', max_length=120)
    customer_log = models.ImageField('логотип заказчика', storage=CustomStorage)
    location = models.CharField('место проекта', max_length=50)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "проект"
        verbose_name_plural = "проекты"    