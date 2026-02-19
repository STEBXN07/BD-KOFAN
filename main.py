from fastapi import FastAPI
from routers import auth
from routers import salones # <--- Su nuevo router

# 1. PRIMERO: Nace la App (ESTO VA ARRIBA)
app = FastAPI()

# 2. SEGUNDO: Ahora sí le pegamos los routers
app.include_router(salones.router) # <--- Ahora sí funciona porque "app" ya existe
app.include_router(auth.router)