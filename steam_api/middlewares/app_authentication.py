import logging
from django.core.cache import cache
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed

from steam_api.models.app_user import AppUser

class AppAuthentication(BaseAuthentication):
    def authenticate(self, request):
        try:
            bearer_token = request.headers.get("Authorization", None)

            if bearer_token is None:
                raise NotAuthenticated("Missing token!")
            
            token = bearer_token.replace("Bearer ", "")
            session_data = cache.get(f"app_session:access:{token}", default=None)

            if session_data is None:
                raise AuthenticationFailed("Verify token failed!")
            
            user = AppUser.objects.get(mini_app_user_id=session_data["user_id"])
            
            return (user, token)
        except Exception as e:
            logging.getLogger().info("MiniAppAuthentication.authenticate exc=%s", e)
            raise AuthenticationFailed("Verify token failed!")