"""
Paso 3 del Tutorial 03: La API View (El Controlador).
Reutiliza la Capa de Servicio: la API es un nuevo cliente del mismo CompraService.
"""
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from .serializers import OrdenInputSerializer, LibroSerializer
from tienda_app.models import Libro
from tienda_app.services import CompraService
from tienda_app.infra.factories import PaymentFactory


def _get_request_data(request):
    """Obtiene los datos del POST: body JSON o form. Acepta también body en raw con Content-Type text/plain."""
    if request.data:
        return request.data
    if not request.body:
        return {}
    # Fallback: cliente envió JSON pero con Content-Type text/plain (ej. Postman en "Text")
    content_type = (request.content_type or "").split(";")[0].strip().lower()
    if content_type in ("application/json", "text/plain", "") or request.body.strip().startswith(b"{"):
        try:
            return json.loads(request.body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            pass
    return {}


class ProductosAPIView(APIView):
    """GET /api/v1/productos/ — catálogo servido por Django (prueba de coexistencia v1)."""

    permission_classes = [AllowAny]

    def get(self, request):
        libros = Libro.objects.all().order_by("id")
        return Response(LibroSerializer(libros, many=True).data)


@method_decorator(csrf_exempt, name="dispatch")
class CompraAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    """
    Endpoint para procesar compras vía JSON.
    GET: muestra formulario para probar. POST: crea la compra.
    Payload POST: { "libro_id": 1, "direccion_envio": "Calle 123" }
    """
    def get(self, request):
        """Muestra un formulario HTML cuando abres el enlace en el navegador."""
        html = """
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"><title>API Comprar</title></head>
        <body style="font-family:sans-serif; max-width:500px; margin:2rem auto; padding:1rem;">
        <h1>API: Comprar</h1>
        <p>Envía un <strong>POST</strong> con <code>libro_id</code> y <code>direccion_envio</code>.</p>
        <form method="post" action="">
            <p><label>libro_id: <input type="number" name="libro_id" value="1" min="0" required></label></p>
            <p><label>direccion_envio: <input type="text" name="direccion_envio" value="Calle 123" size="40" required></label></p>
            <p><button type="submit">Enviar POST (comprar)</button></p>
        </form>
        <p><a href="/">Ver inventario</a></p>
        </body>
        </html>
        """
        from django.http import HttpResponse
        return HttpResponse(html, content_type="text/html; charset=utf-8")

    def post(self, request):
        # 1. Validación de datos de entrada (Adapter)
        data = _get_request_data(request)
        serializer = OrdenInputSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        datos = serializer.validated_data

        try:
            # 2. Inyección de Dependencias (Factory)
            gateway = PaymentFactory.get_processor()
            # 3. Ejecución de Lógica de Negocio (Service Layer)
            servicio = CompraService(procesador_pago=gateway)
            resultado = servicio.ejecutar_compra(
                libro_id=datos["libro_id"],
                cantidad=1,
                usuario=request.user if request.user.is_authenticated else None,
                direccion_envio=datos["direccion_envio"],
            )
            return Response(
                {
                    "estado": "exito",
                    "mensaje": f"Orden creada. Total: {float(resultado)}",
                },
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_409_CONFLICT,
            )
        except Exception as e:
            from django.conf import settings
            body = {"error": "Error interno"}
            if getattr(settings, "DEBUG", False):
                body["detalle"] = str(e)
            return Response(body, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
