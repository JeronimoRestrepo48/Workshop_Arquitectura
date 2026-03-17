from django.db import models
from django.conf import settings


class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.titulo

class Inventario(models.Model):
    libro = models.OneToOneField(Libro, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

class Orden(models.Model):
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, null=True, blank=True,
                             help_text="Opcional cuando la orden se crea con el Builder (usuario + productos).")
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="ordenes_tienda",
    )
    direccion_envio = models.CharField(max_length=500, default="", blank=True)