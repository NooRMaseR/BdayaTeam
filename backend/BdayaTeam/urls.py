"""
URL configuration for BdayaTeam project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from core.middleware import GraphQLAuthMiddleware
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from django.urls import path, include
# from django.conf import settings
from django.contrib import admin


urlpatterns = (
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/organizer/", include("organizer.urls")),
    path("api/technical/", include("technical.urls")),
    path("api/member/", include("member.urls")),
    path('api/admin/', admin.site.urls),
    path("api/", include("core.urls")),
    path("api/graphql/", csrf_exempt(GraphQLView.as_view(graphiql=True, middleware=[GraphQLAuthMiddleware()]))),
)

# if settings.DEBUG:
#     from debug_toolbar.toolbar import debug_toolbar_urls
#     from django.conf.urls.static import static
    
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += debug_toolbar_urls()
