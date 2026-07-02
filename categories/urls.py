from django.urls import path
from .views import CategoryListView

# Definição das rotas exclusivas para o gerenciamento de categorias
urlpatterns = [
    # Rota raiz do app que será consumida pelo frontend (ex: para popular um <select> no formulário)
    path("", CategoryListView.as_view(), name="category-list"),
]