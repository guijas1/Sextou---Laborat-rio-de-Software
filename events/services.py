from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import APIException

from registrations.models import Registration

from .models import Comment


class CapacidadeError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Evento lotado."
    default_code = "evento_lotado"


class InscricaoDuplicadaError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Voce ja esta inscrito."
    default_code = "inscricao_duplicada"


class InscricaoNaoEncontradaError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Voce nao possui inscricao neste evento."
    default_code = "inscricao_nao_encontrada"


class ComentarioVazioError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "O comentario nao pode estar vazio."
    default_code = "comentario_vazio"


@transaction.atomic
def inscrever_usuario(evento, usuario):
    inscricao = Registration.objects.filter(evento=evento, usuario=usuario).first()

    if inscricao and inscricao.status == "confirmada":
        raise InscricaoDuplicadaError()

    if evento.vagas_disponiveis <= 0:
        raise CapacidadeError()

    if inscricao:
        inscricao.status = "confirmada"
        inscricao.save(update_fields=["status"])
        return inscricao

    return Registration.objects.create(evento=evento, usuario=usuario, status="confirmada")


@transaction.atomic
def cancelar_inscricao(evento, usuario):
    inscricao = Registration.objects.filter(
        evento=evento,
        usuario=usuario,
        status="confirmada",
    ).first()

    if not inscricao:
        raise InscricaoNaoEncontradaError()

    inscricao.status = "cancelada"
    inscricao.save(update_fields=["status"])
    return inscricao


def listar_comentarios(evento):
    return Comment.objects.filter(evento=evento).select_related("autor")


def criar_comentario(evento, autor, texto):
    texto = (texto or "").strip()
    if not texto:
        raise ComentarioVazioError()

    return Comment.objects.create(evento=evento, autor=autor, texto=texto)
