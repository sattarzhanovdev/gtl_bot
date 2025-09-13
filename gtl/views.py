# gtl/views.py
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .auth_utils import verify_webapp_init_data, create_jwt
from .models import UserProfile, GameSession, Purchase, MiningAsset, UserAsset
from .serializers import ProfileSerializer, SessionSerializer, PurchaseSerializer, AssetSerializer, UserAssetSerializer

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiTypes

from .serializers import ProfileSerializer

@extend_schema(
    tags=["auth"],
    description="Верифицирует Telegram WebApp initData и возвращает JWT + профиль.",
    request={
        "application/json": {
            "type": "object",
            "properties": {"initData": {"type": "string"}},
            "required": ["initData"],
        }
    },
    responses={
        200: OpenApiTypes.OBJECT,  # можно указать сериалайзер
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            "Успех",
            value={"jwt": "eyJhbGciOiJI...", "profile": {"tg_id": 123, "username": "dan", "level": 1, "total_gtl": 0}},
            response_only=True,
        )
    ],
    auth=[],  # эта ручка без авторизации
)

# ======= AUTH =======
@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])  # без SessionAuth/CSRF
def auth_telegram_webapp(request):
    init_data = request.data.get("initData")
    if not init_data:
        return Response({"error": "initData required"}, status=400)
    try:
        params = verify_webapp_init_data(init_data)
    except ValueError as e:
        return Response({"error": f"Bad signature: {e}"}, status=401)

    user_json = params.get("user")
    if not user_json:
        return Response({"error": "No user"}, status=400)

    try:
        user = json.loads(user_json)  # в initData поле user — это JSON-строка
    except json.JSONDecodeError:
        return Response({"error": "user parse error"}, status=400)

    tg_id = int(user["id"])
    username = user.get("username")
    display_name = (user.get("first_name", "") + " " + user.get("last_name", "")).strip() or username

    profile, _ = UserProfile.objects.get_or_create(
        tg_id=tg_id,
        defaults={"username": username, "display_name": display_name}
    )
    profile.ensure_referral_code()
    if username and profile.username != username:
        profile.username = username
    if display_name and profile.display_name != display_name:
        profile.display_name = display_name
    profile.save()

    token = create_jwt({"sub": str(tg_id), "username": username or ""})
    return Response({"jwt": token, "profile": ProfileSerializer(profile).data})

# ======= PROFILE =======

@api_view(["GET"])
def me(request):
    if not getattr(request, "user_profile", None):
        return Response({"detail": "Unauthorized"}, status=401)
    return Response(ProfileSerializer(request.user_profile).data)

# ======= GAME =======
@extend_schema(tags=["game"], summary="Старт сессии", responses={200: OpenApiTypes.OBJECT})
@api_view(["POST"])
def game_start(request):
    if not getattr(request, "user_profile", None):
        return Response({"detail": "Unauthorized"}, status=401)
    p = request.user_profile
    duration = settings.GAME_FREE_SECONDS if not p.has_starter_pack else 30  # 30с для демо
    s = GameSession.objects.create(user=p, duration_sec=duration)
    return Response(SessionSerializer(s).data)

@api_view(["POST"])
def game_finish(request, session_id: int):
    if not getattr(request, "user_profile", None):
        return Response({"detail": "Unauthorized"}, status=401)
    try:
        s = GameSession.objects.get(id=session_id, user=request.user_profile)
    except GameSession.DoesNotExist:
        return Response({"error": "No session"}, status=404)

    if s.is_finished:
        return Response(SessionSerializer(s).data)

    now = timezone.now()
    elapsed = (now - s.started_at).total_seconds()
    if elapsed < 0 or elapsed > s.duration_sec + 2:  # небольшой буфер
        return Response({"error": "Duration mismatch"}, status=400)

    payload = request.data.get("payload", {})  # {"total_gtl": int, "minerals": {"H": 3, ...}, "clicks_per_sec": float}
    total_gtl = int(payload.get("total_gtl", 0))
    cps = float(payload.get("clicks_per_sec", 0))

    # анти‑чит: ограничим максимум
    if cps > settings.CLICK_RATE_LIMIT:
        total_gtl = 0
        payload["flag"] = "rate_limit"

    s.collected_gtl = max(0, min(total_gtl, 100000))
    s.payload = payload
    s.is_finished = True
    s.save()

    # обновим профиль
    p = request.user_profile
    p.total_gtl += s.collected_gtl
    # обновим периодическую таблицу
    minerals = payload.get("minerals", {})
    pt = p.periodic_table or {}
    for sym, qty in minerals.items():
        pt[sym] = int(pt.get(sym, 0)) + int(qty)
    p.periodic_table = pt

    # переход уровней (упрощенно)
    if p.level == 1 and p.has_starter_pack:
        p.level = 2
    p.save()

    return Response(SessionSerializer(s).data)

# ======= SHOP =======
SHOP_ITEMS = [
    {
        "key": "pickaxe_1",
        "title": "Кирка 1 (базовая)",
        "price": 10,
        "grants_starter": True,
        "image": "/static/images/kirka1.png"
    },
    {
        "key": "pickaxe_2",
        "title": "Кирка 2 (мощная)",
        "price": 100,
        "grants_starter": True,
        "image": "/static/images/kirka2.png"
    },
    {
        "key": "dynamite_1",
        "title": "Динамит 1",
        "price": 50,
        "grants_starter": True,
        "image": "/static/images/dinamit1.png"
    },
    {
        "key": "dynamite_2",
        "title": "Динамит 2",
        "price": 80,
        "grants_starter": True,
        "image": "/static/images/dinamit2.png"
    },
    {
        "key": "golden_foot",
        "title": "Золотой отпечаток (магнит)",
        "price": 120,
        "grants_starter": True,
        "image": "/static/images/magnitnye botinki.png"
    },
    # {
    #     "key": "boot_basic",
    #     "title": "Ботинки базовые",
    #     "price": 40,
    #     "grants_starter": False,
    #     "image": "/static/images/boot_basic.png"
    # },
    {
        "key": "magnit_boots",
        "title": "Магнитный отпечаток",
        "price": 40,
        "grants_starter": False,
        "image": "/static/images/magnit_boot.png"
    },
]

@extend_schema(tags=["shop"], summary="Список товаров", responses={200: OpenApiTypes.OBJECT})
@api_view(["GET"])
def shop_items(request):
    return Response({"items": SHOP_ITEMS})

@api_view(["POST"])
def shop_buy(request):
    if not getattr(request, "user_profile", None):
        return Response({"detail": "Unauthorized"}, status=401)
    key = request.data.get("item_key")
    it = next((i for i in SHOP_ITEMS if i["key"] == key), None)
    if not it:
        return Response({"error": "Unknown item"}, status=400)
    p = request.user_profile
    price = it["price"]
    if p.balance < price:
        return Response({"error": "Not enough balance"}, status=400)
    p.balance -= price
    if it.get("grants_starter"):
        p.has_starter_pack = True
    p.save()
    purchase = Purchase.objects.create(user=p, item_key=key, price=price)
    return Response({"ok": True, "purchase": PurchaseSerializer(purchase).data, "profile": ProfileSerializer(p).data})

# ======= PERIODIC TABLE =======
PT_MINERALS = ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne"]  # прототип: 10 элементов

@api_view(["GET"])
def periodic_table(request):
    if not getattr(request, "user_profile", None):
        return Response({"detail": "Unauthorized"}, status=401)
    return Response({"symbols": PT_MINERALS, "collected": request.user_profile.periodic_table or {}})

# ======= REFERRAL =======
@api_view(["GET"])
def referral(request):
    if not getattr(request, "user_profile", None):
        return Response({"detail": "Unauthorized"}, status=401)
    me = request.user_profile
    me.ensure_referral_code(); me.save()
    link = f"https://t.me/YOUR_BOT?start={me.referral_code}"
    return Response({"code": me.referral_code, "link": link, "count": me.referrals_count})

# ======= ASSETS (иконка №8) =======
@api_view(["GET"])
def assets_list(request):
    assets = MiningAsset.objects.all()
    return Response({"assets": AssetSerializer(assets, many=True).data})

@api_view(["POST"])
def assets_buy(request):
    if not getattr(request, "user_profile", None):
        return Response({"detail": "Unauthorized"}, status=401)
    key = request.data.get("key")
    try:
        a = MiningAsset.objects.get(key=key)
    except MiningAsset.DoesNotExist:
        return Response({"error": "Unknown asset"}, status=404)
    p = request.user_profile
    if p.balance < a.price:
        return Response({"error": "Not enough balance"}, status=400)
    p.balance -= a.price
    p.save()
    ua = UserAsset.objects.create(user=p, asset=a)
    return Response({"ok": True, "item": UserAssetSerializer(ua).data, "profile": ProfileSerializer(p).data})

# ======= EXCHANGE (симуляция) =======
@api_view(["POST"])
def exchange(request):
    if not getattr(request, "user_profile", None):
        return Response({"detail": "Unauthorized"}, status=401)
    amount = int(request.data.get("amount", 0))
    p = request.user_profile
    if amount <= 0 or amount > p.total_gtl:
        return Response({"error": "Invalid amount"}, status=400)
    p.total_gtl -= amount
    p.balance += amount // 10  # условный курс 10:1 во внутреннюю валюту
    p.save()
    return Response({"ok": True, "profile": ProfileSerializer(p).data})


