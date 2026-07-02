from django.conf import settings
from django.db import models


class Event(models.Model):
    """Evento criado por um usuário organizador."""
    STATUS = [
        ("rascunho", "Rascunho"),
        ("publicado", "Publicado"),
        ("encerrado", "Encerrado"),
    ]

    titulo = models.CharField(max_length=140)
    descricao = models.TextField()
    data_hora = models.DateTimeField()
    local = models.CharField(max_length=200)
    capacidade_maxima = models.PositiveIntegerField()
    imagem_capa = models.ImageField(upload_to="capas/", blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS, default="publicado")
    criado_em = models.DateTimeField(auto_now_add=True)

    organizador = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="eventos"
    )
    categoria = models.ForeignKey(
        "categories.Category", on_delete=models.PROTECT, related_name="eventos"
    )

    class Meta:
        ordering = ["data_hora"]

    def __str__(self):
        return self.titulo

    @property
    def inscritos(self):
        return self.inscricoes.filter(status="confirmada").count()

    @property
    def vagas_disponiveis(self):
        return max(0, self.capacidade_maxima - self.inscritos)


class Comment(models.Model):
    """Comentário de um usuário em um evento."""
    evento = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="comentarios")
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["data"]
