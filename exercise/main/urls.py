from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    PostViewSet,
    CustomTokenLoginView,
    SourceViewSet,
    RandomQuoteView,
    TopQuotesView,
    LikeDislikeView,
)
from django.contrib.auth import views as auth_views
from users.views import RegisterView, ProfileView

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="posts")
router.register(r"sources", SourceViewSet, basename="sources")
router.register(
    r"posts/add-quote",
    PostViewSet.add_quote,
    basename="posts_add",
)
urlpatterns = [
    path("api/", include(router.urls)),
    path("auth/token/login/", CustomTokenLoginView.as_view(), name="login"),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    # Аутентификация пользователей
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("", RandomQuoteView.as_view(), name="random_quote"),
    path("top/", TopQuotesView.as_view(), name="top_quotes"),
    path(
        "vote/<int:pk>/<str:action>/", LikeDislikeView.as_view(), name="vote"
    ),
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
]
