from rest_framework import serializers
from .models import Registration
from events.serializers import EventSerializer 

# Formata os dados da tabela de inscrição para o frontend consumir
class RegistrationSerializer(serializers.ModelSerializer):
    # Aninha o serializer de eventos para devolver o objeto completo do evento em vez de apenas o seu ID.
    # Isso poupa o React de ter que fazer um 'fetch' extra na API para cada card de evento listado.
    evento = EventSerializer(read_only=True)

    class Meta:
        model = Registration
        fields = ["id", "evento", "status", "data_inscricao"]