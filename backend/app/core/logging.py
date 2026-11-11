import logging
import re

# Si un mensaje contiene "password=algo" o "token: algo", el valor se oculta.
PATRON_SENSIBLE = re.compile(
    r"(?i)(password|contrasena|token|authorization|secret|cookie)(\s*[=:]\s*)([^\s,;&]+)"
)


class FiltroDatosSensibles(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        mensaje = record.getMessage()
        record.msg = PATRON_SENSIBLE.sub(r"\1\2[OCULTO]", mensaje)
        record.args = ()
        return True


def configurar_logging(nivel: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    handler.addFilter(FiltroDatosSensibles())

    raiz = logging.getLogger()
    raiz.handlers = [handler]
    raiz.setLevel(nivel)

    # SQLAlchemy puede imprimir los parámetros de las consultas: lo limitamos.
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
