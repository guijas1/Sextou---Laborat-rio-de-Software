from rest_framework import serializers
from django.contrib.auth.models import User 

# Serializer focado no registro básico de usuários
class RegisterSerializer(serializers.ModelSerializer):
    # Campo configurado como write_only para garantir que a senha não seja exposta em respostas JSON
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    # Validação customizada para impedir duplicidade de e-mails no banco de dados
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este e-mail já está cadastrado.")
        return value

    # Sobrescrita do método create para instanciar o usuário corretamente com hash na senha
    def create(self, validated_data):
        username = validated_data.get("username") or validated_data.get("email")
        
        user = User.objects.create_user(
            username=username,
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", "")
        )
        return user


# Serializer genérico para leitura e envio de dados não sensíveis ao frontend
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


# Serializer completo para registro, alinhado com os requisitos de payload do React
class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name"]
        extra_kwargs = {
            'password': {'write_only': True} 
        }

    # Assegura a unicidade do usuário validando tanto o campo email quanto o username
    def validate_email(self, value):
        if User.objects.filter(email=value).exists() or User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este e-mail já está cadastrado.")
        return value

    # Utiliza o gerenciador do Django para criar o usuário e aplicar a criptografia da senha
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', '')
        )
        return user

    # Modela a saída do JSON para bater exatamente com as chaves que o frontend espera receber
    def to_representation(self, instance):
        return {
            "id": instance.id,
            "username": instance.username,
            "email": instance.email,
            "first_name": instance.first_name,
            "nome": instance.first_name
        }