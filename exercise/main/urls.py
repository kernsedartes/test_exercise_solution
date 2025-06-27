from django.contrib import admin
from django.urls import include, path
from .views import PostViewSet, CustomTokenLoginView

urlpatterns = [
    path("auth/token/login/", CustomTokenLoginView.as_view(), name="login"),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path("", include(router.urls)),
]
