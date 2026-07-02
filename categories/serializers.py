from rest_framework import serializers
from .models import Category

# Transforma as instâncias do banco de dados em JSON estruturado para a API
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'