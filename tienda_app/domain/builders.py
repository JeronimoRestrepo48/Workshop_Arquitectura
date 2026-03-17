"""
Patrón Builder: construcción paso a paso de órdenes de dominio.
Encapsula el cálculo de totales e IVA y valida datos antes de persistir.
"""
from ..models import Orden

IVA = 1.19


class OrdenBuilder:
    """Construye una Orden con interfaz fluida (Fluent Interface)."""

    def __init__(self):
        self.reset()

    def reset(self):
        self._usuario = None
        self._items = []
        self._direccion = ""

    def con_usuario(self, usuario):
        self._usuario = usuario
        return self

    def con_productos(self, productos):
        """productos: lista de objetos con atributo .precio (ej. Libro)."""
        self._items = list(productos)
        return self

    def para_envio(self, direccion):
        self._direccion = direccion or ""
        return self

    def build(self) -> Orden:
        if not self._usuario or not self._items:
            raise ValueError("Datos insuficientes para crear la orden.")

        subtotal = sum(float(p.precio) for p in self._items)
        total_con_iva = subtotal * IVA

        orden = Orden.objects.create(
            usuario=self._usuario,
            total=total_con_iva,
            direccion_envio=self._direccion,
        )
        self.reset()
        return orden
