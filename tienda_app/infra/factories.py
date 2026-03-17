"""
Factory Method: centraliza la decisión de qué procesador de pago usar.
La configuración viene del ambiente (PAYMENT_PROVIDER), no del código.
"""
import os
from .gateways import BancoNacionalProcesador
from ..domain.interfaces import ProcesadorPago


class MockPaymentProcessor(ProcesadorPago):
    """Implementación ligera para pruebas (Mocking). No realiza cargo real."""
    def pagar(self, monto: float) -> bool:
        print(f"[DEBUG] Mock Payment: Procesando pago de ${monto} sin cargo real.")
        return True


class PaymentFactory:
    """Fabrica el procesador de pago según variable de entorno."""
    @staticmethod
    def get_processor() -> ProcesadorPago:
        provider = os.getenv("PAYMENT_PROVIDER", "BANCO")

        if provider == "MOCK":
            return MockPaymentProcessor()

        return BancoNacionalProcesador()
