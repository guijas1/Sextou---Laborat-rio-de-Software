from django.db import models


class Category(models.Model):
    """Categoria de evento (ex.: Festa, Show, Workshop)."""
    nome = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=60, unique=True)

    class Meta:
        verbose_name = "categoria"
        verbose_name_plural = "categorias"
        ordering = ["nome"]

    def __str__(self):
        return self.nome
