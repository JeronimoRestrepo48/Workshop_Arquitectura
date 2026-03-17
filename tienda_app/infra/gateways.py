import datetime
from ..domain.interfaces import ProcesadorPago

class BancoNacionalProcesador(ProcesadorPago):
    """
    Implementación concreta de la infraestructura.
    Simula un banco local escribiendo en un log.
    """
    def pagar(self, monto: float) -> bool:
        # SUSTITUYA "JERONIMO_MORESTREPO_ANGEL" por su nombre y apellido real
        archivo_log = "pagos_locales_JERONIMO_MORESTREPO_ANGEL.log"
        with open(archivo_log, "a") as f:
            f.write(f"[{datetime.datetime.now()}] Transaccion exitosa por: ${monto}\n")
        return True