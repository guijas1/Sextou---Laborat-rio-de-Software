import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Event
from .permissions import IsOrganizerOrReadOnly
from .serializers import CommentSerializer, EventSerializer
from .services import (
    cancelar_inscricao,
    criar_comentario,
    inscrever_usuario,
    listar_comentarios,
)

logger = logging.getLogger(__name__)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.select_related("organizador", "categoria").prefetch_related(
        "comentarios__autor",
    )
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOrganizerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(organizador=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Event create validation failed: %s", serializer.errors)
            return Response(
                {"detail": "Nao foi possivel criar o evento.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            logger.warning("Event update validation failed: %s", serializer.errors)
            return Response(
                {"detail": "Nao foi possivel atualizar o evento.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def vacancies(self, request, pk=None):
        evento = self.get_object()
        return Response({"vagas_disponiveis": evento.vagas_disponiveis})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def register(self, request, pk=None):
        evento = self.get_object()
        inscrever_usuario(evento, request.user)
        return Response({"mensagem": "Inscricao confirmada!"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        evento = self.get_object()
        cancelar_inscricao(evento, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["get", "post"],
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def comments(self, request, pk=None):
        evento = self.get_object()

        if request.method == "GET":
            serializer = CommentSerializer(listar_comentarios(evento), many=True)
            return Response(serializer.data)

        comentario = criar_comentario(
            evento=evento,
            autor=request.user,
            texto=request.data.get("texto"),
        )
        return Response(CommentSerializer(comentario).data, status=status.HTTP_201_CREATED)
