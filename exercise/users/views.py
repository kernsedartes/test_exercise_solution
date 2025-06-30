from django.shortcuts import render
from django.contrib.auth import login
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.contrib.auth.views import LoginView, LogoutView
from .models import User
from .forms import CustomUserCreationForm, CustomLoginForm
from main.models import Post
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.contrib.auth import logout


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("main:random_quote")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ["first_name", "last_name", "email"]
    template_name = "registration/profile.html"
    success_url = reverse_lazy("main:profile")

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Статистика пользователя
        context["liked_posts"] = Post.objects.filter(liked_by=user).count()
        context["added_posts"] = Post.objects.filter(added_by=user).count()
        context["total_views"] = (
            Post.objects.filter(added_by=user).aggregate(total_views=Sum("views"))[
                "total_views"
            ]
            or 0
        )

        return context


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = "registration/login.html"


class CustomLogoutView(LogoutView):
    template_name = "registration/logout.html"
    next_page = reverse_lazy("main:random_quote")

    def post(self, request, *args, **kwargs):
        # Для JWT - инвалидация токена
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            pass  # Пропускаем если нет JWT токена

        # Стандартный логаут Django
        logout(request)

        # Для API-клиентов
        if request.accepts("application/json"):
            return Response({"detail": "Successfully logged out."})

        return super().post(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        request.session.flush()  # Полная очистка сессии
        return response
