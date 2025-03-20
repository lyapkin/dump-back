import re
import requests
import logging
from rest_framework import serializers
from .signals import request_save_handlers
from django.conf import settings

from .models import *


logger = logging.getLogger("visota.forms")


class CommonSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        logger.info("Starts saving to db")
        try:
            result = super().create(validated_data)
        except Exception as e:
            logger.info(f"Saving failed. {repr(e)}")
            raise e
        logger.info("Ends saving to db")
        return result

    def validate_number(self, number):
        result = re.match(r"^\+\d{9,15}$", number) or re.match(r"^\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}$", number)
        if result is None:
            raise serializers.ValidationError("Номер телефона указан неверно")

        return number

    def run_validation(self, data):
        logger.info("Runs validation")
        # logger.info(f"Initial data: {data}")
        try:
            result = super().run_validation(data)
        except serializers.ValidationError as e:
            logger.warning(f"ValidationError, {e.get_full_details()}")
            raise e
        except Exception as e:
            logger.error(repr(e))
            raise e
        logger.info("Ends validation")

        self.validate_grecaptcha(data.get("grecaptcha"))
        return result

    def validate_grecaptcha(self, token):
        logger.info("Starts grecaptcha validation.")

        if token is None:
            logger.warning("Grecaptcha token is None")
            raise serializers.ValidationError(
                {"global": ["Формы временно недоступны, попробуйте связаться с нами другим способом"]}
            )

        data = {"secret": settings.RECAPTCHA_SECRET_KEY, "response": token}
        try:
            logger.info(f"Starts request for grecaptcha verification")

            res = requests.post("https://www.google.com/recaptcha/api/siteverify", params=data)
            data = res.json()

            logger.info(f"Ends request for grecaptcha verification; status: {res.status_code}; data: {data}")
        except Exception as e:
            logger.error(f"Fails request for grecaptcha verification. {repr(e)}")
            # raise serializers.ValidationError(
            #     {"global": ["Формы временно не работают, попробуйте связаться с нами другим способом"]}
            # )
            return

        # if res.status_code != 200:
        #     raise serializers.ValidationError({"global": ["Что-то пошло не так, попробуйте еще раз"]})

        if not data["success"] and (
            "invalid-input-response"
            in data["error-codes"]
            # or "timeout-or-duplicate" in data["error-codes"]
        ):
            logger.warning("Grecaptcha validation faild.")
            raise serializers.ValidationError(
                {"global": ["Формы временно недоступны, попробуйте связаться с нами другим способом"]}
            )

        if data["success"] and data["score"] <= 0.5:
            logger.warning("Grecaptcha validation faild.")
            raise serializers.ValidationError(
                {"global": ["Формы временно недоступны, попробуйте связаться с нами другим способом"]}
            )

        logger.info("Ends grecaptcha validation.")


class ConsultationRequestSerializer(CommonSerializer):
    class Meta:
        model = ConsultationRequest
        exclude = ("date",)


class OfferRequestSerializer(CommonSerializer):
    class Meta:
        model = CommercialOfferRequest
        exclude = ("date",)


class PriceRequestSerializer(CommonSerializer):
    class Meta:
        model = PriceRequest
        exclude = ("date",)


class ProductOrderSerializer(serializers.ModelSerializer):
    # order_price = serializers.SerializerMethodField('get_current_price')

    class Meta:
        model = ProductOrder
        fields = ("product", "count", "order_price")

    # def get_current_price(self, productOrder):
    #     print(type(productOrder))
    #     current_price = productOrder.product.current_price
    #     return current_price


class OrderSerializer(CommonSerializer):
    products = ProductOrderSerializer(many=True)

    class Meta:
        model = Order
        fields = (
            "name",
            "number",
            # 'email',
            # 'comment',
            # 'delivery_address',
            # 'payment_method',
            "products",
        )

    # def validate_payment_method(self, method):
    #     if (method != 'cash') and (method != 'non-cash'):
    #         raise serializers.ValidationError('Выберите способ оплаты')
    #     return method

    def validate_products(self, products):
        products_dict = {}
        for p in products:
            products_dict[p["product"].id] = p["order_price"]
        queryset = Product.objects.filter(pk__in=map(lambda product: product["product"].id, products))
        for p in queryset.iterator():
            logger.info(
                f"Validating product price. current price: {p.current_price}, order price: {products_dict[p.id]}"
            )
            if p.current_price != products_dict[p.id]:
                raise serializers.ValidationError(
                    "Цена на один или несколько продуктов изменилась. Перезагрузите страницу."
                )
        return products

    def create(self, validated_data):
        products = validated_data.pop("products")
        ModelClass = self.Meta.model
        instance = ModelClass.objects.create(**validated_data)
        ProductOrder.objects.bulk_create([ProductOrder(**product, order=instance) for product in products])
        request_save_handlers.order_ready.send(ModelClass, instance=instance, created=True)

        return instance


class SampleRequestSerializer(CommonSerializer):
    class Meta:
        model = SampleRequest
        exclude = ("date",)
