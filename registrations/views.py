from rest_framework import generics, permissions
from .models import Registration
from .serializers import RegistrationSerializer

# View genérica para listar apenas as inscrições pertencentes ao usuário que fez a requisição
class MyRegistrationsListView(generics.ListAPIView):
    serializer_class = RegistrationSerializer
    # Exige token JWT válido na requisição; visitantes deslogados recebem erro 401 automático
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Otimização crítica de banco de dados (select_related) para evitar o problema de N+1 queries.
        # Como o serializer aninha os dados, o Django faz um JOIN no SQL e traz tudo em uma única consulta rápida.
        return Registration.objects.filter(
            usuario=self.request.user
        ).select_related("evento", "evento__organizador", "evento__categoria")