from django.contrib.auth import get_user_model
from rest_framework import serializers

from categories.models import Category
from registrations.models import Registration

from .models import Comment, Event

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    autor = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "autor", "texto", "data"]


class EventSerializer(serializers.ModelSerializer):
    categoria = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Category.objects.all(),
    )
    organizador = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )
    inscritos = serializers.SerializerMethodField()
    ja_inscrito = serializers.SerializerMethodField()
    comentarios = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = "__all__"

    def get_inscritos(self, obj):
        return Registration.objects.filter(evento=obj, status="confirmada").count()

    def get_ja_inscrito(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Registration.objects.filter(
                evento=obj,
                usuario=request.user,
                status="confirmada",
            ).exists()
        return False
