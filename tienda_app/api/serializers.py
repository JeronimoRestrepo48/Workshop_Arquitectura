"""
Paso 2 del Tutorial 03: El Adaptador (Serializer).
Transforma modelos y objetos de dominio en JSON. Actúa como DTO para validar entrada.
"""
from rest_framework import serializers
from tienda_app.models import Libro, Orden


def _stock_actual(libro):
    """Obtiene el stock actual del libro desde Inventario (campo calculado)."""
    from tienda_app.models import Inventario
    try:
        inv = Inventario.objects.get(libro=libro)
        return inv.cantidad
    except Inventario.DoesNotExist:
        return 0


class LibroSerializer(serializers.ModelSerializer):
    """Serializer para Libro; stock_actual viene de la relación con Inventario."""
    stock_actual = serializers.SerializerMethodField()

    class Meta:
        model = Libro
        fields = ["id", "titulo", "precio", "stock_actual"]

    def get_stock_actual(self, obj):
        return _stock_actual(obj)


class OrdenInputSerializer(serializers.Serializer):
    """
    Serializer para VALIDAR la entrada de datos, no ligado a un modelo.
    Actúa como un DTO (Data Transfer Object).
    """
    libro_id = serializers.IntegerField()
    direccion_envio = serializers.CharField(max_length=200)
