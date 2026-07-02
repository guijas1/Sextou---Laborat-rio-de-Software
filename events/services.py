from django.db import transaction
from rest_framework.exceptions import APIException
from rest_framework import status

# Exceções customizadas para padronizar os erros HTTP 400 devolvidos à interface
class CapacidadeError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Evento lotado."
    default_code = "evento_lotado"

class InscricaoDuplicadaError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Você já está inscrito."
    default_code = "inscricao_duplicada"

# Garante que a lógica de inscrição seja executada de forma atômica no banco, evitando race conditions no momento do clique
@transaction.atomic
def inscrever_usuario(evento, usuario):
    from registrations.models import Registration

    if Registration.objects.filter(evento=evento, usuario=usuario, status="confirmada").exists():
        raise InscricaoDuplicadaError()
    if evento.vagas_disponiveis <= 0:
        raise CapacidadeError()
        
    return Registration.objects.create(evento=evento, usuario=usuario, status="confirmada")