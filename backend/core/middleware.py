from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser

class GraphQLAuthMiddleware:

    def resolve(self, next, root, info, **kwargs):
        request = info.context
        if request.user.is_authenticated:
            return next(root, info, **kwargs)
        
        try:
            token_auth = CookiesJWTAuthentication()
            user_token_auth = token_auth.authenticate(request)
            
            if user_token_auth:
                info.context.user = user_token_auth[0]
            else:
                info.context.user = AnonymousUser()
        except AuthenticationFailed:
            info.context.user = AnonymousUser()
        
        return next(root, info, **kwargs)


class CookiesJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is not None:
            raw_token = self.get_raw_token(header)
        else:
            raw_token = request.COOKIES.get('access_token')
            
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except:
            return None