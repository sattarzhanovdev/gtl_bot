# gtl/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("auth/telegram-webapp", views.auth_telegram_webapp),
    path("me", views.me),

    path("game/start", views.game_start),
    path("game/finish/<int:session_id>", views.game_finish),

    path("shop/items", views.shop_items),
    path("shop/buy", views.shop_buy),

    path("periodic", views.periodic_table),
    path("referral", views.referral),

    path("assets", views.assets_list),
    path("assets/buy", views.assets_buy),

    path("exchange", views.exchange),
]
