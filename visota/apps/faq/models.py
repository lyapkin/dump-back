from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


# Create your models here.
class FAQCategory(models.Model):
    name = models.CharField("категория вопроса", max_length=50, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "категория вопроса"
        verbose_name_plural = "категории вопроса"


class FAQ(models.Model):
    question = models.CharField("вопрос", max_length=255, unique=True)
    answer = CKEditor5Field("ответ", config_name='extends')
    categories = models.ManyToManyField(FAQCategory, related_name="faqs", verbose_name="категории вопроса")

    def __str__(self):
        return self.question
    
    class Meta:
        verbose_name = "вопрос"
        verbose_name_plural = "вопросы"
