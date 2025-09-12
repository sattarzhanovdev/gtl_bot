# gtl/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from .auth_utils import decode_jwt
from .models import UserProfile

class JWTAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth.split(" ", 1)[1]
            try:
                data = decode_jwt(token)
                request.user_profile = UserProfile.objects.get(tg_id=int(data["sub"]))
            except Exception:
                return JsonResponse({"detail": "Unauthorized"}, status=401)
        else:
            request.user_profile = None
        return None