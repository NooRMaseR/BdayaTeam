from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser

class GraphQLAuthMiddleware:

    def resolve(self, next, root, info, **kwargs):
        request = info.context
        if request.user.is_authenticated:
            return next(root, info, **kwargs)
        
        try:
            token_auth = TokenAuthentication()
            user_token_auth = token_auth.authenticate(request)
            
            if user_token_auth:
                info.context.user = user_token_auth[0]
            else:
                info.context.user = AnonymousUser()
        except AuthenticationFailed:
            info.context.user = AnonymousUser()
        
        return next(root, info, **kwargs)
