import getpass

from app.core.db import SessionLocal
from app.modules.funcionarios.models import Rol
from app.modules.funcionarios.service import FuncionarioService


def main() -> None:
    username = input("Usuario: ").strip()
    nombre = input("Nombre completo: ").strip()
    rol = Rol(input("Rol (funcionario/encargado): ").strip())
    password = getpass.getpass("Contraseña: ")

    with SessionLocal() as db:
        usuario = FuncionarioService(db).crear_usuario(username, nombre, password, rol)
        print(f"Usuario creado: {usuario.username} ({usuario.rol.value})")


if __name__ == "__main__":
    main()
