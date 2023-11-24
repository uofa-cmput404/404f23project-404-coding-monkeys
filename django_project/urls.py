"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg import openapi
from rest_framework import permissions
import connections

import accounts

# https://episyche.com/blog/how-to-create-django-api-documentation-using-swagger
schema_view = get_schema_view(
    openapi.Info(
        title="ChimpChat API Documentation",
        default_version='v1',),
    public=True,
    permission_classes=(permissions.IsAuthenticatedOrReadOnly,),
)

full_schema_view = get_schema_view(
    openapi.Info(
        title="Full ChimpChat API Documentation",
        default_version='v1',),
    public=True,
    permission_classes=(permissions.IsAuthenticatedOrReadOnly,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("accounts.urls")), # if accounts request, forward to accounts.urls (login, logout, signup)
    path("accounts/", include("django.contrib.auth.urls")), # include built-in authorization app
    path("posts/", include("posts.urls")), # if posts request, forward to posts.urls (creation, detail)
    path("connections/", include("connections.urls")), # if connections request, forward to connections.urls (follow, unfollow
    # path("inbox/", include("inbox.urls")), # if inbox request, forward to inbox.urls (follow, unfollow
    path("", include("pages.urls")), # goto pages.urls if generic request 
    path('api/', schema_view.with_ui('swagger', cache_timeout=0),name='schema-swagger-ui'),
    path('full/docs', connections.views.docs_viewer, name='markdown_docs'),
    path('extra/docs', connections.views.extra_docs_viewer, name='docs_extra'),

    path('api/token/', accounts.views.generate_jwt_token, name='get_token'),
    # path('fullDocs/', full_schema_view.with_ui('swagger', cache_timeout=0),name='full-schema-swagger-ui')
]
