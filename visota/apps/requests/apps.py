from django.apps import AppConfig
from django.db.models.signals import post_save


class RequestsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.requests"
    verbose_name = "запросы клиентов"

    def ready(self):
        from .signals import request_save_handlers
        from .models import ConsultationRequest, CommercialOfferRequest, PriceRequest, Order, SampleRequest

        post_save.connect(
            request_save_handlers.send_mail_on_create,
            sender=ConsultationRequest,
            weak=False,
            dispatch_uid="ConsultationRequestModelFromClientRequestsApp",
        )

        post_save.connect(
            request_save_handlers.send_mail_on_create,
            sender=CommercialOfferRequest,
            weak=False,
            dispatch_uid="OfferRequestModelFromClientRequestsApp",
        )

        post_save.connect(
            request_save_handlers.send_mail_on_create,
            sender=PriceRequest,
            weak=False,
            dispatch_uid="PriceRequestModelFromClientRequestsApp",
        )

        request_save_handlers.order_ready.connect(
            request_save_handlers.send_mail_on_create,
            sender=Order,
            weak=False,
            dispatch_uid="OrderModelFromClientRequestsApp",
        )

        post_save.connect(
            request_save_handlers.send_mail_on_create,
            sender=SampleRequest,
            weak=False,
            dispatch_uid="SampleRequestModelFromClientRequestsApp",
        )
