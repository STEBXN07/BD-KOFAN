"""
Script para crear el primer usuario en la base de datos.

Ejecuta esto UNA SOLA VEZ cuando no tienes usuarios en la colección "users".
Después podrás hacer login con este usuario y crear clientes.

CÓMO EJECUTARLO:
  1. Abre la terminal (PowerShell o CMD) en la carpeta del proyecto BD-KOFAN.
  2. Activa el entorno virtual:  .\venv\Scripts\activate
  3. Ejecuta:  python crear_usuario.py
  4. Si ves "Usuario creado correctamente", revisa en MongoDB la base kofan_reservas,
     colección "users" (o "usuarios"): debería aparecer 1 documento.
"""
from db.client import db
from core.security import hash_password

# Usuario que se creará (puedes cambiar estos valores)
USERNAME = "admin"
PASSWORD = "admin123"   # Contraseña en texto claro; se guardará hasheada
ROLE = "admin"

def main():
    collection = db.users

    # Si ya existe un usuario con este username, no lo creamos de nuevo
    if collection.find_one({"username": USERNAME}):
        print(f"Ya existe un usuario con username '{USERNAME}'. No se creó nada.")
        print("Puedes hacer login con ese usuario.")
        return

    # Hashear la contraseña (igual que cuando la API crea usuarios)
    password_hasheada = hash_password(PASSWORD)

    nuevo_usuario = {
        "username": USERNAME,
        "password": password_hasheada,
        "role": ROLE,
    }

    collection.insert_one(nuevo_usuario)
    print("Usuario creado correctamente en la base de datos.")
    print()
    print("Para hacer login usa:")
    print(f"  Username: {USERNAME}")
    print(f"  Password: {PASSWORD}")
    print()
    print("1. POST http://127.0.0.1:8000/auth/login")
    print("   Body tipo Form: username = admin, password = admin123")
    print("2. Copia el 'access_token' de la respuesta.")
    print("3. POST http://127.0.0.1:8000/clientes/ con header:")
    print("   Authorization: Bearer <pega_el_token>")
    print("   Body JSON con los datos del cliente.")


if __name__ == "__main__":
    main()
