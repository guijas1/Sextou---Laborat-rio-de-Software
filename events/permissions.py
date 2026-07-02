from rest_framework import permissions

# Trava de segurança no backend para garantir que apenas o dono do evento possa alterá-lo
class IsOrganizerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Libera o acesso para requisições que não alteram dados (como o front lendo a página de detalhes)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Bloqueia a edição ou exclusão caso o usuário logado não seja o organizador do evento
        return obj.organizador == request.user