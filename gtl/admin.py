from django.contrib import admin
from .models import (
    UserProfile, Purchase, GameSession, MiningAsset, UserAsset
)

# ---------- Inlines ----------
class PurchaseInline(admin.TabularInline):
    model = Purchase
    extra = 0
    readonly_fields = ("item_key", "price", "created_at")

class GameSessionInline(admin.TabularInline):
    model = GameSession
    extra = 0
    readonly_fields = ("started_at", "duration_sec", "is_finished", "collected_gtl", "payload")

class UserAssetInline(admin.TabularInline):
    model = UserAsset
    extra = 0
    readonly_fields = ("asset", "acquired_at")
    autocomplete_fields = ("asset",)

# ---------- UserProfile ----------
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("tg_id", "username", "display_name", "level", "total_gtl", "balance",
                    "has_starter_pack", "referrals_count", "updated_at")
    search_fields = ("tg_id", "username", "display_name", "referral_code")
    list_filter = ("has_starter_pack", "level")
    readonly_fields = ("created_at", "updated_at", "periodic_table")
    inlines = [PurchaseInline, GameSessionInline, UserAssetInline]
    ordering = ("-updated_at",)

# ---------- Purchase ----------
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "item_key", "price", "created_at")
    search_fields = ("item_key", "user__username", "user__tg_id")
    list_filter = ("item_key", "created_at")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at",)

# ---------- GameSession ----------
@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "started_at", "duration_sec", "is_finished", "collected_gtl")
    search_fields = ("user__username", "user__tg_id")
    list_filter = ("is_finished",)
    autocomplete_fields = ("user",)
    readonly_fields = ("started_at",)

# ---------- MiningAsset ----------
@admin.register(MiningAsset)
class MiningAssetAdmin(admin.ModelAdmin):
    list_display = ("key", "title", "country", "price", "monthly_yield_pct")
    search_fields = ("key", "title", "country")
    list_filter = ("country",)
    ordering = ("country", "title")

# ---------- UserAsset ----------
@admin.register(UserAsset)
class UserAssetAdmin(admin.ModelAdmin):
    list_display = ("user", "asset", "acquired_at")
    search_fields = ("user__username", "user__tg_id", "asset__title")
    autocomplete_fields = ("user", "asset")
    readonly_fields = ("acquired_at",)