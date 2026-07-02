from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer, UserSerializer, UserRegisterSerializer
from django.contrib.auth import get_user_model  


# View baseada em classe para lidar com a criação de novos usuários via API
class RegisterView(APIView):
    # Libera o acesso para usuários não autenticados poderem se registrar
    permission_classes = [permissions.AllowAny]

    # Processa o payload recebido e salva no banco caso as validações do serializer passem
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Usuário cadastrado com sucesso!"}, 
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"detail": "Não foi possível cadastrar o usuário.", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# View para recuperar as informações do usuário atual logado
class UserMeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    # Bloqueia a rota, exigindo um token JWT válido no cabeçalho da requisição
    permission_classes = [permissions.IsAuthenticated]
    
    # Extrai a instância do usuário a partir do token de autenticação
    def get_object(self):
        return self.request.user


# Alternativa genérica do DRF para criação de usuários, simplificando o fluxo de registro
class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    # Rota pública para permitir novos cadastros
    permission_classes = [AllowAny]