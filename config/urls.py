from django.contrib import admin
from django.urls import path, include

# Roteador central do backend: recebe os pedidos do frontend e encaminha para as rotas específicas de cada módulo
urlpatterns = [
    # Painel nativo do Django para administração rápida da base de dados
    path("admin/", admin.site.urls),
    
    # Endpoints de consumo de dados da API
    path("api/", include("events.urls")),
    path("api/registrations/", include("registrations.urls")), 
    path("api/categories/", include("categories.urls")),
    
    # Endpoints dedicados à autenticação e gestão de utilizadores
    path("accounts/", include("accounts.urls")),
]