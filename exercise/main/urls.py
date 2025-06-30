from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from users.views import (
    RegisterView,
    ProfileView,
    CustomLoginView,
    CustomLogoutView,
)
from .views import (
    PostViewSet,
    SourceViewSet,
    RandomQuoteView,
    TopQuotesView,
    LikeDislikeView,
)

app_name = "main"

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="posts")
router.register(r"sources", SourceViewSet, basename="sources")

urlpatterns = [
    # ============ Ваши кастомные вьюхи ============
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    # Смена пароля
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/password_change.html"
        ),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html"
        ),
        name="password_change_done",
    ),
    # ============ Djoser API ============
    path("api/auth/", include("djoser.urls.jwt")),  # Только если используете JWT
    path("api/auth/register/", include("djoser.urls.base")),
    # ============ Основные вьюхи ============
    path("", RandomQuoteView.as_view(), name="random_quote"),
    path("top/", TopQuotesView.as_view(), name="top_quotes"),
    path("vote/<int:pk>/<str:action>/", LikeDislikeView.as_view(), name="vote"),
    path(
        "add-quote/",
        PostViewSet.as_view({"get": "add_quote_form", "post": "add_quote"}),
        name="add_quote",
    ),
    # ============ API Endpoints ============
    path("api/", include(router.urls)),
]
