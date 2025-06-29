from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from djoser.serializers import TokenCreateSerializer
from .models import Post, Source
from users.models import User
from django.contrib.auth import authenticate


class CustomTokenCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            email=attrs.get("email"), password=attrs.get("password")
        )

        if not user:
            raise serializers.ValidationError(
                {"auth_token": ["Неверные учетные данные"]}
            )

        self.user = user

        refresh = RefreshToken.for_user(user)
        return {
            "auth_token": str(refresh.access_token),
        }


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = (
            "id",
            "quote",
            "weight",
            "likes",
            "dislikes",
            "source",
        )

    def create(self, validated_data):
        if Source.objects.filter(name=validated_data.source.name).exists():
            post = Post.objects.create()
            return post

    def validate(self, data):
        quote = data.get("quote")
        if quote:
            if self.instance:
                if (
                    Post.objects.exclude(pk=self.instance.pk)
                    .filter(quote__iexact=quote)
                    .exists()
                ):
                    raise serializers.ValidationError(
                        "Такая цитата уже существует"
                    )
            else:
                if Post.objects.filter(quote__iexact=quote).exists():
                    raise serializers.ValidationError(
                        "Такая цитата уже существует"
                    )

        source = data.get(
            "source", self.instance.source if self.instance else None
        )
        if source:
            post_count = source.post_set.exclude(
                pk=self.instance.pk if self.instance else None
            ).count()

            if post_count >= 3:
                raise serializers.ValidationError(
                    f"Источник '{source.name}' уже имеет максимальное количество цитат (3)"
                )

        return data


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = "__all__"

    def validate_name(self, value):
        if Source.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError(
                "Источник с таким именем уже существует"
            )
        return value


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        if "password" not in data:
            raise serializers.ValidationError(
                {"password": "This field is required."}
            )
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
