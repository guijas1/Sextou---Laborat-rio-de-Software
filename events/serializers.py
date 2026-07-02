from rest_framework import serializers
from .models import Event
from categories.models import Category
from registrations.models import Registration 
from django.contrib.auth import get_user_model

User = get_user_model()

# Serializer responsável por moldar o JSON dos eventos que será consumido pelo React
class EventSerializer(serializers.ModelSerializer):
    # Transforma a chave estrangeira em um slug ou username legível no payload da resposta
    categoria = serializers.SlugRelatedField(
        slug_field='slug', 
        queryset=Category.objects.all()
    )
    organizador = serializers.SlugRelatedField(
        slug_field='username', 
        read_only=True
    )
    
    # Campos extras que não existem fisicamente na tabela, mas o frontend precisa renderizar
    inscritos = serializers.SerializerMethodField()
    ja_inscrito = serializers.SerializerMethodField()
    comentarios = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    # Calcula o total de inscritos diretamente na serialização do objeto
    def get_inscritos(self, obj):
        return Registration.objects.filter(evento=obj).count()

    # Descobre se o usuário que fez a requisição via token já está inscrito no evento que visualiza
    def get_ja_inscrito(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Registration.objects.filter(evento=obj, usuario=request.user).exists()
        return False
    
    # Embuti a lista de comentários dentro do próprio JSON do evento para reduzir as chamadas de rede no frontend
    def get_comentarios(self, obj):
        from .models import Comment 
        
        comentarios_salvos = Comment.objects.filter(evento=obj)
        
        return [
            {
                "id": c.id, 
                "autor": c.autor.username, 
                "texto": c.texto
            } 
            for c in comentarios_salvos
        ]
