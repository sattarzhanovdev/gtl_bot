# gtl/serializers.py
from rest_framework import serializers
from .models import UserProfile, GameSession, Purchase, MiningAsset, UserAsset

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["tg_id", "username", "display_name", "level", "total_gtl",
                  "balance", "has_starter_pack", "periodic_table", "referrals_count", "referral_code"]

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = ["id", "started_at", "duration_sec", "is_finished", "collected_gtl", "payload"]

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ["id", "item_key", "price", "created_at"]

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MiningAsset
        fields = ["key", "title", "country", "lat", "lng", "price", "monthly_yield_pct"]

class UserAssetSerializer(serializers.ModelSerializer):
    asset = AssetSerializer()
    class Meta:
        model = UserAsset
        fields = ["asset", "acquired_at"]