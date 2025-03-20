from django.db import models

from common.utils import CustomStorage

# Create your models here.
class Bonus(models.Model):
    condition = models.CharField('условие для бонуса', max_length=60)
    bonus1 = models.CharField('бонус', max_length=50)
    bonus2 = models.CharField('бонус', max_length=50, null=True, blank=True)
    bonus3 = models.CharField('бонус', max_length=50, null=True, blank=True)

    def __str__(self):
        return str(self.id) + ' ' + self.condition
    
    class Meta:
        verbose_name = 'дополнительный бонус к акциям'
        verbose_name_plural = "дополнительные бонусы к акциям" 


class Promo(models.Model):
    title = models.CharField('заголовок акции', max_length=100, unique=True)
    additional_text = models.CharField('текст под заголовком', max_length=100)
    last_day = models.DateField('последний день акции')
    img = models.ImageField('картинка акции', storage=CustomStorage)
    is_active = models.BooleanField('акция активна', default=True)
    bonus = models.ForeignKey(Bonus, models.SET_NULL, null=True, blank=True, verbose_name='дополнительные бонусы')

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Акция на товар'
        verbose_name_plural = "Акции на товар"
