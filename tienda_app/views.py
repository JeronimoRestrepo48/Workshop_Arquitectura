import datetime
from django.views import View
from django.shortcuts import render, HttpResponse, get_object_or_404
from .models import Libro, Inventario, Orden
from .services import CompraService, CompraRapidaService
from .domain.logic import CalculadorImpuestos
from .infra.factories import PaymentFactory


def inventario_view(request):
    """
    Vista HTML de inventario: lista libros con su stock actual.
    Al comprar por API o por HTML, esta vista refleja el cambio (misma lógica de negocio).
    """
    items = Inventario.objects.select_related("libro").all().order_by("libro__titulo")
    return render(request, "tienda_app/inventario.html", {"items": items})


def compra_rapida_fbv(request, libro_id):
    """Paso 1: FBV Spaghetti - múltiples responsabilidades en la vista."""
    libro = get_object_or_404(Libro, id=libro_id)

    if request.method == 'POST':
        # VIOLACION SRP: Lógica de inventario en la vista
        inventario = Inventario.objects.get(libro=libro)
        if inventario.cantidad > 0:
            # VIOLACION OCP: Cálculo de negocio hardcoded
            total = float(libro.precio) * 1.19

            # VIOLACION DIP: Proceso de pago acoplado al filesystem
            with open("pagos_manuales.log", "a") as f:
                f.write(f"[{datetime.datetime.now()}] Pago FBV: ${total}\n")

            inventario.cantidad -= 1
            inventario.save()
            Orden.objects.create(libro=libro, total=total)

            return HttpResponse(f"Compra exitosa: {libro.titulo}")
        else:
            return HttpResponse("Sin stock", status=400)

    total_estimado = float(libro.precio) * 1.19
    return render(request, 'tienda_app/compra_rapida.html', {
        'libro': libro,
        'total': total_estimado
    })


class CompraRapidaView(View):
    """
    Paso 2/3: CBV que delega en CompraRapidaService.
    Menos de 10 líneas de lógica; toda la complejidad está en el servicio.
    """
    template_name = 'tienda_app/compra_rapida.html'

    def get(self, request, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)
        return render(request, self.template_name, {'libro': libro, 'total': total})

    def post(self, request, libro_id):
        servicio = CompraRapidaService(procesador_pago=PaymentFactory.get_processor())
        try:
            total = servicio.procesar(libro_id)
            return HttpResponse(f"Comprado via CBV. Total: ${total}") if total else HttpResponse("Error", status=400)
        except ValueError as e:
            return HttpResponse(str(e), status=400)


class CompraView(View):
    """
    CBV: Vista Basada en Clases. 
    Actúa como un "Portero": recibe la petición y delega al servicio.
    """
    template_name = 'tienda_app/compra.html'

    def setup_service(self):
        gateway = PaymentFactory.get_processor()
        return CompraService(procesador_pago=gateway)

    def get(self, request, libro_id):
        servicio = self.setup_service()
        contexto = servicio.obtener_detalle_producto(libro_id)
        return render(request, self.template_name, contexto)

    def post(self, request, libro_id):
        servicio = self.setup_service()
        try:
            total = servicio.ejecutar_compra(libro_id, cantidad=1)
            return render(request, self.template_name, {
                'mensaje_exito': f"¡Gracias por su compra! Total: ${total}",
                'total': total
            })
        except (ValueError, Exception) as e:
            return render(request, self.template_name, {'error': str(e)}, status=400)