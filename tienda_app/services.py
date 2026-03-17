from django.shortcuts import get_object_or_404
from .models import Libro, Inventario, Orden
from .domain.logic import CalculadorImpuestos
from .domain.builders import OrdenBuilder


class CompraRapidaService:
    """
    Paso 3: Capa de Servicio para Compra Rápida.
    Orquesta dominio (IVA), infra (pago) y persistencia (inventario, orden).
    """
    def __init__(self, procesador_pago):
        self.procesador_pago = procesador_pago

    def procesar(self, libro_id):
        libro = Libro.objects.get(id=libro_id)
        inv = Inventario.objects.get(libro=libro)

        if inv.cantidad <= 0:
            raise ValueError("No hay existencias.")

        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)

        if self.procesador_pago.pagar(total):
            inv.cantidad -= 1
            inv.save()
            Orden.objects.create(libro=libro, total=total)
            return total
        return None


class CompraService:
    """
    SERVICE LAYER: Orquesta la interacción entre el dominio,
    la infraestructura y la base de datos.
    """
    def __init__(self, procesador_pago):
        self.procesador_pago = procesador_pago
        self.builder = OrdenBuilder()

    def ejecutar_proceso_compra(self, usuario, lista_productos, direccion=""):
        """Uso del Builder: semántica clara y validación interna."""
        orden = (
            self.builder
            .con_usuario(usuario)
            .con_productos(lista_productos)
            .para_envio(direccion)
            .build()
        )
        if self.procesador_pago.pagar(float(orden.total)):
            return f"Orden {orden.id} procesada exitosamente."
        orden.delete()
        raise Exception("Error en la pasarela de pagos.")

    def obtener_detalle_producto(self, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)
        return {"libro": libro, "total": total}

    def ejecutar_compra(self, libro_id, cantidad=1, usuario=None, direccion_envio=None):
        # 1. Obtener datos
        libro = get_object_or_404(Libro, id=libro_id)
        inv = get_object_or_404(Inventario, libro=libro)

        # 2. Validar Reglas de Negocio
        if inv.cantidad < cantidad:
            raise ValueError("No hay suficiente stock para completar la compra.")

        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)

        # 3. Procesar Infraestructura (Pago)
        pago_exitoso = self.procesador_pago.pagar(total)
        
        if not pago_exitoso:
            raise Exception("La transacción fue rechazada por el banco.")

        # 4. Persistencia de efectos secundarios
        inv.cantidad -= cantidad
        inv.save()
        
        Orden.objects.create(
            libro=libro,
            total=total,
            usuario=usuario,
            direccion_envio=direccion_envio or "",
        )
        
        return total