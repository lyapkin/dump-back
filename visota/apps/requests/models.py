from typing import Any, Iterable
from django.db import models
from django.core.validators import MinValueValidator
from apps.products.models import Product


# Create your models here.
class ConsultationRequest(models.Model):
    name = models.CharField("контактное лицо", max_length=100)
    number = models.CharField("номер телефона", max_length=20)
    # comment = models.TextField("комментарий", blank=True, null=True)
    # activity_type = models.CharField("вид деятельности", max_length=50, null=True, blank=True)
    # company_name = models.CharField("наименование предприятия или И.П.", max_length=100, null=True, blank=True)
    date = models.DateTimeField("дата", auto_now_add=True)

    def __str__(self):
        return "Запрос консультации " + str(self.name) + " - " + str(self.number) + " - " + str(self.date)

    class Meta:
        verbose_name = "запрос консультации"
        verbose_name_plural = "запросы консультаций"


class CommercialOfferRequest(models.Model):
    name = models.CharField("контактное лицо", max_length=100)
    number = models.CharField("номер телефона", max_length=20)
    date = models.DateTimeField("дата", auto_now_add=True)

    def __str__(self):
        return "Запрос коммерческого предложения " + str(self.name) + " - " + str(self.number) + " - " + str(self.date)

    class Meta:
        verbose_name = "запрос коммерческого предложения"
        verbose_name_plural = "запросы коммерческих предложений"


class PriceRequest(models.Model):
    name = models.CharField("контактное лицо", max_length=100)
    number = models.CharField("номер телефона", max_length=20)
    # email = models.EmailField('адрес электронной почты', max_length=254)
    # comment = models.TextField("комментарий", blank=True, null=True)
    date = models.DateTimeField("дата", auto_now_add=True)
    product = models.ForeignKey(Product, verbose_name="товар", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "Запрос цены " + str(self.name) + " " + str(self.product.name) + " " + str(self.date)

    class Meta:
        verbose_name = "запрос цены"
        verbose_name_plural = "запросы цен"


class Order(models.Model):
    name = models.CharField("контактное лицо", max_length=100)
    number = models.CharField("номер телефона", max_length=20)
    # email = models.EmailField('адрес электронной почты', max_length=254)
    # comment = models.TextField("комментарий", blank=True, null=True)
    # delivery_address = models.CharField('адрес доставки', max_length=200)
    date = models.DateTimeField("дата", auto_now_add=True)

    def __str__(self):
        return "Заказ " + str(self.name) + " " + str(self.date)

    class Meta:
        verbose_name = "заказ"
        verbose_name_plural = "заказы"


class ProductOrder(models.Model):
    product = models.ForeignKey(Product, verbose_name="товар", on_delete=models.SET_NULL, null=True)
    count = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="количество заказанного товара")
    order_price = models.IntegerField(
        validators=[MinValueValidator(1)], verbose_name="цена единицы товара на момент заказа"
    )
    order = models.ForeignKey(Order, verbose_name="данные заказа", on_delete=models.CASCADE, related_name="products")

    def __str__(self):
        return "Заказ товара " + str(self.product.name) + " " + str(self.count) + " " + str(self.order_price)

    class Meta:
        verbose_name = "заказанный товар"
        verbose_name_plural = "заказвнныеы товары"


class SampleRequest(models.Model):
    name = models.CharField("контактное лицо", max_length=100)
    number = models.CharField("номер телефона", max_length=20)
    # email = models.EmailField('адрес электронной почты', max_length=254)
    # entity = models.CharField("юр. лицо", max_length=200)
    # card = models.CharField('карта партнера', max_length=200)
    date = models.DateTimeField("дата", auto_now_add=True)

    def __str__(self):
        return "Заказ " + str(self.name) + " " + str(self.date)

    class Meta:
        verbose_name = "запрос на образцы продукции"
        verbose_name_plural = "запросы на образцы продукции"
