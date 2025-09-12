from django.apps import AppConfig

class GtlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gtl'

    def ready(self):
        from .models import MiningAsset
        if not MiningAsset.objects.exists():
            MiningAsset.objects.get_or_create(key='oil_sa', defaults=dict(title='Нефть', country='Саудовская Аравия', lat=24.0, lng=45.0, price=120, monthly_yield_pct=20))
            MiningAsset.objects.get_or_create(key='gas_ru', defaults=dict(title='Газ', country='Россия', lat=61.5, lng=105.3, price=100, monthly_yield_pct=15))
            MiningAsset.objects.get_or_create(key='oil_us', defaults=dict(title='Нефть', country='США', lat=37.1, lng=-95.7, price=140, monthly_yield_pct=18))
# И не забыть в INSTALLED_APPS использовать "gtl.apps.GtlConfig".
