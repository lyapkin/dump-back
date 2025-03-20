from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


# Create your models here.
class Vacancy(models.Model):
    name = models.CharField("наименование", max_length=100, unique=True)
    slug = models.SlugField("url", max_length=110, unique=True)
    description = CKEditor5Field("текст вакансии", config_name='extends')
    is_open = models.BooleanField('вакансия открыта', default=True)
    last_modified = models.DateTimeField("дата изменения", auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "вакансия"
        verbose_name_plural = "вакансии"
