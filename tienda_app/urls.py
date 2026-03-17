from django.urls import path
from .views import inventario_view, CompraView, CompraRapidaView, compra_rapida_fbv
from .api.views import CompraAPIView

urlpatterns = [
    path("", inventario_view, name="inventario"),
    path("inventario/", inventario_view, name="inventario_alt"),
    path("compra/<int:libro_id>/", CompraView.as_view(), name="finalizar_compra"),
    path("compra-rapida-fbv/<int:libro_id>/", compra_rapida_fbv, name="compra_rapida_fbv"),
    path("compra-rapida/<int:libro_id>/", CompraRapidaView.as_view(), name="compra_rapida"),
    path("api/v1/comprar/", CompraAPIView.as_view(), name="api_comprar"),
]