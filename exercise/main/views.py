from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db import models
from rest_framework import status, viewsets, permissions
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .pagination import CustomPagination
from .models import Post, Source, Vote
from users.models import User
from .forms import AddQuoteForm
from .serializers import (
    UserCreateSerializer,
    UserSerializer,
    SourceSerializer,
    PostSerializer,
)
import random


class CustomTokenLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response(
                {"auth_token": ["Неверные учетные данные"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {"auth_token": str(refresh.access_token)},
            status=status.HTTP_200_OK,
        )


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        post = self.get_object()
        post.likes += 1
        post.save()
        return Response({"status": "liked", "likes": post.likes})

    @action(detail=True, methods=["post"])
    def dislike(self, request, pk=None):
        post = self.get_object()
        post.dislikes += 1
        post.save()
        return Response({"status": "disliked", "dislikes": post.dislikes})

    @action(detail=False, methods=["get"])
    def top(self, request):
        top_quotes = Post.objects.order_by("-likes")[:10]
        serializer = self.get_serializer(top_quotes, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def add_quote_form(self, request):
        sources = Source.objects.all()
        form = AddQuoteForm()
        context = {
            "sources": sources,
            "form": form,
            "user": request.user,
        }
        print("Rendering add_quote_form")
        print("User authenticated:", request.user.is_authenticated)
        print("Sources count:", sources.count())
        print("Form fields:", form.fields.keys())
        return render(request, "main/add_quote.html", context)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def add_quote_form(self, request):
        sources = Source.objects.all()
        form = AddQuoteForm()
        context = {
            "sources": sources,
            "form": form,
            "user": request.user,
        }
        print("Rendering add_quote_form")
        print("User authenticated:", request.user.is_authenticated)
        print("Sources count:", sources.count())
        print("Form fields:", form.fields.keys())
        return render(request, "main/add_quote.html", context)

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def add_quote(self, request):
        try:
            if not request.user.is_authenticated:
                print("User not authenticated")
                return Response(
                    {"error": "Authentication required"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            form = AddQuoteForm(request.POST)
            print("POST data:", request.POST)
            print("Form valid:", form.is_valid())
            if not form.is_valid():
                print("Form errors:", form.errors.as_json())

            if form.is_valid():
                post = form.save(commit=False)
                post.added_by = request.user
                post.save()
                messages.success(request, "Цитата успешно добавлена!")
                print("Redirecting to main:random_quote")
                return redirect("main:random_quote")

            sources = Source.objects.all()
            print("Re-rendering form with errors")
            return render(
                request,
                "main/add_quote.html",
                {
                    "sources": sources,
                    "form": form,
                    "user": request.user,
                },
            )

        except Exception as e:
            print("Exception in add_quote:", str(e))
            if request.accepts("application/json"):
                return Response(
                    {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
                )
            messages.error(request, f"Ошибка: {str(e)}")
            return redirect("main:add_quote")


class SourceViewSet(viewsets.ModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    pagination_class = CustomPagination


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAdminUser]

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return super().get_serializer(*args, **kwargs)

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        user = serializer.instance
        response_data = {
            "email": user.email,
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "password": user.pasword,
        }
        headers = self.get_success_headers(serializer.data)
        return Response(
            response_data, status=status.HTTP_201_CREATED, headers=headers
        )


class RandomQuoteView(View):
    def get(self, request):
        posts = Post.objects.all().select_related("source")
        print("Rendering RandomQuoteView with template: index.html")
        print("Posts count:", posts.count())
        if not posts.exists():
            print("No posts found")
            return render(
                request, "index.html", {"error": "Нет цитат в базе данных"}
            )
        weights = [post.weight for post in posts]
        random_post = random.choices(list(posts), weights=weights, k=1)[0]
        Post.objects.filter(pk=random_post.pk).update(
            views=models.F("views") + 1
        )
        random_post.views += 1
        total_views = (
            Post.objects.aggregate(total_views=models.Sum("views"))[
                "total_views"
            ]
            or 0
        )
        print("Selected post:", random_post.quote)
        return render(
            request,
            "index.html",
            {"post": random_post, "total_views": total_views},
        )


class TopQuotesView(View):

    def get(self, request):
        top_quotes = Post.objects.order_by("-likes").select_related("source")[
            :10
        ]
        total_views = (
            Post.objects.aggregate(total_views=models.Sum("views"))[
                "total_views"
            ]
            or 0
        )

        return render(
            request,
            "top_quotes.html",
            {"quotes": top_quotes, "total_views": total_views},
        )


class LikeDislikeView(View):
    def post(self, request, pk, action):
        if not request.user.is_authenticated:
            return redirect("main:login")

        post = get_object_or_404(Post, pk=pk)
        if action not in ["like", "dislike"]:
            return redirect(
                request.META.get("HTTP_REFERER", "main:random_quote")
            )

        existing_vote = Vote.objects.filter(
            user=request.user, post=post
        ).first()

        if existing_vote:
            if existing_vote.vote_type == action:
                existing_vote.delete()
                if action == "like":
                    post.likes -= 1
                    post.liked_by.remove(request.user)
                else:
                    post.dislikes -= 1
            else:
                if existing_vote.vote_type == "like":
                    post.likes -= 1
                    post.liked_by.remove(request.user)
                    post.dislikes += 1
                else:
                    post.dislikes -= 1
                    post.likes += 1
                    post.liked_by.add(request.user)
                existing_vote.vote_type = action
                existing_vote.save()
        else:
            Vote.objects.create(user=request.user, post=post, vote_type=action)
            if action == "like":
                post.likes += 1
                post.liked_by.add(request.user)
            else:
                post.dislikes += 1

        post.save()
        return redirect(request.META.get("HTTP_REFERER", "main:random_quote"))
