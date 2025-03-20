import logging
from smtplib import SMTPAuthenticationError, SMTPException
from django.core.mail import send_mail
from ..models import *
from django.dispatch import Signal

from ..tasks import pass_request_to_email

# print(__name__)
# logger = logging.getLogger(__name__)
# print(logger)


order_ready = Signal()


def send_mail_on_create(sender, instance=None, created=False, **kwargs):
    if created:
        if sender is ConsultationRequest:
            subject = "Запрос консультации: " + instance.name + " - " + instance.number
            message = (
                f"Запрос консультации.\n\n"
                f"Контактное лицо: {instance.name}\n" + f"Номер телефона: {instance.number}\n"
                # f'Наименование предприятия или И.П.: {instance.company_name}\n' +
                # f'Вид деятельности: {instance.activity_type}\n' +
                # f'Комментарий: {instance.comment}\n'
            )
        elif sender is CommercialOfferRequest:
            subject = "Запрос коммерческого предложения: " + instance.name + " - " + instance.number
            message = (
                f"Запрос коммерческого предложения.\n\n"
                f"Контактное лицо: {instance.name}\n" + f"Номер телефона: {instance.number}\n"
                #    f'Наименование предприятия или И.П.: {instance.company_name}\n' +
                #    f'Вид деятельности: {instance.activity_type}\n' +
                #    f'Комментарий: {instance.comment}\n'
            )
        elif sender is PriceRequest:
            subject = "Запрос цены: " + instance.product.name + " - " + instance.number
            message = (
                f"Запрос цены.\n\n"
                f"Контактное лицо: {instance.name}\n" + f"Номер телефона: {instance.number}\n"
                # + f"Email: {instance.email}\n"
                + f"Товар: {instance.product.name}\n" + f"Артикул: {instance.product.code}\n"
                # + f"Комментарий: {instance.comment}\n"
            )
        elif sender is Order:
            subject = "Заказ продукции: " + instance.name + " - " + instance.number
            message = (
                f"Заказ продукции.\n\n"
                f"Контактное лицо: {instance.name}\n" + f"Номер телефона: {instance.number}\n"
                # + f"Email: {instance.email}\n"
                # + f"Адрес доставки: {instance.delivery_address}\n"
                # + f"Комментарий: {instance.comment}\n"
                + f"Товары:"
                + f"".join(
                    map(
                        lambda p: f"\n\n Товар: {p.product.name},\n \tАртикул: {p.product.code}\n \tКоличество: {p.count}\n \tЦена на момент заказа: {p.order_price}",
                        instance.products.all(),
                    )
                )
            )
        elif sender is SampleRequest:
            subject = "Запрос бесплатного образца: " + instance.name + " - " + instance.number
            message = (
                f"Запрос бесплатного образца.\n\n"
                f"Контактное лицо: {instance.name}\n" + f"Номер телефона: {instance.number}\n"
                # + f"Email: {instance.email}\n"
                # + f"Юр. лицо: {instance.entity}\n"
                # + f"Карта партнера: {instance.card}\n"
            )

        pass_request_to_email.delay(subject, message)
        # try:
        #     send_mail(
        #         subject,
        #         message,
        #         'd_mal@mail.ru',
        #         ['d_mal@mail.ru'],
        #         fail_silently=False
        #         )
        # except SMTPException as e:
        #     print(e)
