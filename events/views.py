import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Event
from .serializers import EventSerializer
from .permissions import IsOrganizerOrReadOnly

logger = logging.getLogger(__name__)
from registrations.models import Registration 

# ViewSet principal que agrupa toda a lógica de negócio do módulo de eventos
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    # Permite leitura para visitantes, mas exige token JWT válido para criar, editar ou deletar eventos
    permission_classes = [IsAuthenticatedOrReadOnly, IsOrganizerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(organizador=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Event create validation failed: %s", serializer.errors)
            return Response({"detail": "Não foi possível criar o evento.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            logger.warning("Event update validation failed: %s", serializer.errors)
            return Response({"detail": "Não foi possível atualizar o evento.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)
        return Response(serializer.data)

    # Endpoint customizado para processar as inscrições dos usuários
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def register(self, request, pk=None):
        evento_atual = self.get_object() 
        usuario_atual = request.user

        # Validação de segurança para impedir duplicidade de inscrições
        if Registration.objects.filter(evento=evento_atual, usuario=usuario_atual).exists():
            return Response(
                {"erro": "Você já está inscrito neste evento."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Checagem final de disponibilidade de vagas antes de autorizar a inscrição no banco
        inscritos_atuais = Registration.objects.filter(evento=evento_atual).count()
        if inscritos_atuais >= evento_atual.capacidade_maxima:
            return Response(
                {"erro": "Poxa, este evento já está lotado!"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        Registration.objects.create(evento=evento_atual, usuario=usuario_atual)
        return Response({"mensagem": "Inscrição confirmada!"}, status=status.HTTP_201_CREATED)

    # Endpoint customizado para revogar a inscrição do usuário logado
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        evento_atual = self.get_object()
        usuario_atual = request.user

        inscricao = Registration.objects.filter(evento=evento_atual, usuario=usuario_atual).first()
        
        if not inscricao:
            return Response(
                {"erro": "Você não possui inscrição neste evento."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        inscricao.delete()
        # Retorna status 204 (No Content) pois não há dados para devolver à view após o delete
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    # Endpoint específico para processar submissões do formulário de comentários no frontend
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comments(self, request, pk=None):
        evento_atual = self.get_object()
        usuario_atual = request.user
        
        texto_comentario = request.data.get('texto')

        # Valida se o body da requisição possui conteúdo real antes de gravar
        if not texto_comentario:
            return Response(
                {"erro": "O comentário não pode estar vazio."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        from .models import Comment 
        
        novo_comentario = Comment.objects.create(
            evento=evento_atual, 
            autor=usuario_atual, 
            texto=texto_comentario
        )

        # Retorna os dados inseridos de forma instantânea e formatada para o estado do React ser atualizado
        return Response({
            "id": novo_comentario.id,
            "autor": usuario_atual.username, 
            "texto": novo_comentario.texto
        }, status=status.HTTP_201_CREATED)
