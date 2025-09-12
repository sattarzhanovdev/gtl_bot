# gtl/models.py
from django.db import models
from django.utils import timezone

class UserProfile(models.Model):
    tg_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    display_name = models.CharField(max_length=150, blank=True, null=True)

    level = models.PositiveIntegerField(default=1)
    total_gtl = models.PositiveIntegerField(default=0)
    balance = models.PositiveIntegerField(default=100)  # внутр. валюта для магазина
    has_starter_pack = models.BooleanField(default=False)  # куплен ли стартовый аксессуар

    periodic_table = models.JSONField(default=dict)  # {"H": qty, "He": qty, ...}
    referrals_count = models.PositiveIntegerField(default=0)
    referral_code = models.CharField(max_length=16, unique=True, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def ensure_referral_code(self):
        if not self.referral_code:
            import secrets
            self.referral_code = secrets.token_hex(4)

class Purchase(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    item_key = models.CharField(max_length=64)  # e.g. "pickaxe_1"
    price = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class GameSession(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    started_at = models.DateTimeField(default=timezone.now)
    duration_sec = models.PositiveIntegerField(default=10)
    is_finished = models.BooleanField(default=False)
    collected_gtl = models.PositiveIntegerField(default=0)
    payload = models.JSONField(default=dict)  # минералы, события, диагностика

class MiningAsset(models.Model):
    key = models.CharField(max_length=32, unique=True)  # e.g. "oil_sa"
    title = models.CharField(max_length=128)
    country = models.CharField(max_length=64)
    lat = models.FloatField()
    lng = models.FloatField()
    price = models.PositiveIntegerField(default=100)
    monthly_yield_pct = models.PositiveIntegerField(default=10)

class UserAsset(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    asset = models.ForeignKey(MiningAsset, on_delete=models.CASCADE)
    acquired_at = models.DateTimeField(auto_now_add=True)