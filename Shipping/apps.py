from django.apps import AppConfig


class ShippingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Shipping'
    def ready(self):
        from Shipping import signals