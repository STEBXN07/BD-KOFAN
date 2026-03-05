"""
Punto de entrada de la API BD-KOFAN.

Arquitectura: main.py → core (config, security) → db → routers + services + dependencies.
- Login: POST /auth/login → JWT Bearer.
- Usuario: GET /users/me, GET /users/admin (requieren token).
- Clientes: CRUD /clientes (requieren token).
- Eventos/salones: /eventos (salones, reservas).
Documentación: /docs, /redoc.
"""
from fastapi import FastAPI

from routers import auth, clientes, cotizaciones, facturas, salones, users
from routers.tipo_evento import router as tipo_evento_router
from services.tipo_evento_service import seed_tipos_evento

# -----------------------------------------------------------------------------
# Aplicación FastAPI
# -----------------------------------------------------------------------------

app = FastAPI(
    title="BD-KOFAN API",
    description="API para gestión de eventos, reservas y clientes - EcoHotel Kofán",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Inicializa los tipos de evento predefinidos en la base de datos al arrancar el servidor
@app.on_event("startup")
def startup_seed_tipos_evento():
    """Carga catálogo base de tipos de evento al iniciar."""
    seed_tipos_evento()

# -----------------------------------------------------------------------------
# Routers (orden: recursos, auth/users para login, luego clientes)
# -----------------------------------------------------------------------------

app.include_router(salones.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(clientes.router)
app.include_router(cotizaciones.router)
app.include_router(facturas.router)
app.include_router(tipo_evento_router)
