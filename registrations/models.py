from django.conf import settings
from django.db import models


class Registration(models.Model):
    """Inscrição de um usuário em um evento."""
    STATUS = [("confirmada", "Confirmada"), ("cancelada", "Cancelada")]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inscricoes")
    evento = models.ForeignKey("events.Event", on_delete=models.CASCADE, related_name="inscricoes")
    status = models.CharField(max_length=10, choices=STATUS, default="confirmada")
    data_inscricao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("usuario", "evento")

    def __str__(self):
        return f"{self.usuario} → {self.evento}"
