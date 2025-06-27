from django.shortcuts import render
from rest_framework import status, viewsets
from .models import Post
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from .pagination import CustomPagination


class CustomTokenLoginView(APIView):
    permission_classes = [AllowAny]

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
    pagination_class = CustomPagination
