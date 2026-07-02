from rest_framework import generics, permissions
from .models import Category
from .serializers import CategorySerializer

# View genérica focada apenas na entrega de uma lista de itens (somente leitura)
class CategoryListView(generics.ListAPIView):
    # Define a fonte de dados, puxando todas as categorias cadastradas
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    # Rota mantida como pública, permitindo que a interface do React exiba as categorias mesmo para usuários deslogados
    permission_classes = [permissions.AllowAny]