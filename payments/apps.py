from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments'

    def ready(self):
        from .models import ExternalApp
        from django.db.utils import OperationalError, ProgrammingError

        try:
            if not ExternalApp.objects.filter(name="ADMIN_SHOP").exists():
                ExternalApp.objects.create(
                    name="ADMIN_SHOP",
                    api_key="73a2bf1d1ebeaebc2d3a69185ccaad6d7dbe9526f8306f328b2684db999137d3",
                    is_active=True
                )
        except (OperationalError, ProgrammingError):
            # DB not ready (migrations running)
            pass