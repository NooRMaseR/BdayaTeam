from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import AnonymousUser

class GraphQLTokenAuthMiddleware:

    def resolve(self, next, root, info, **kwargs):
        request = info.context
        if request.user.is_authenticated:
            return next(root, info, **kwargs)
        
        auth = TokenAuthentication()
        try:
            userAuth = auth.authenticate(request)
            
            if userAuth:
                info.context.user = userAuth[0]
            else:
                info.context.user = AnonymousUser()
        except:
            info.context.user = AnonymousUser()
        
        return next(root, info, **kwargs)
            

class CookieToTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            token_key = request.COOKIES.get('auth_token')
            
            if token_key:
                request.META['HTTP_AUTHORIZATION'] = f'Token {token_key}'

        return self.get_response(request)