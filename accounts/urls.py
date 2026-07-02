from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserMeView, UserRegisterView

# Mapeamento das rotas de autenticação e gestão de usuários para a API
urlpatterns = [
    # Rotas de cadastro (Atenção: verificar com o front qual das duas rotas de registro será mantida)
    path("register/", RegisterView.as_view(), name="auth_register"),
    path("register/", UserRegisterView.as_view(), name="user_register"),
    
    # Endpoints fornecidos pelo SimpleJWT para emissão e renovação de tokens de acesso
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    # Endpoint utilizado pelo React para carregar os dados do usuário autenticado na sessão
    path("me/", UserMeView.as_view(), name="user_me"),
]