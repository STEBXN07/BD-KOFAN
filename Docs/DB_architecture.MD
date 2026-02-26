# 📚 Arquitectura Base de Datos
## Sistema de Reservas - Hotel Kofán
Versión: 3.0.0  
Base de datos: kofan_reservas  
Motor: MongoDB Atlas  
Backend: FastAPI (Python)

---

# Objetivo

Este documento define la arquitectura base de la base de datos en MongoDB.
Cada integrante del equipo deberá implementar en código las colecciones
que le correspondan según la asignación del proyecto.

⚠️ Este documento NO crea la base de datos.
La base se crea automáticamente cuando se insertan datos desde el backend.

---

# Conexión Remota

Trabajamos en MongoDB Atlas (remoto).

Cada desarrollador debe:
 
1. Tener el archivo `.env`
2. Tener configurado `MONGO_URI`
3. Conectarse al mismo cluster
4. No crear bases de datos locales

---

# 🔄 Diferencia entre MySQL y MongoDB

Es importante entender que MongoDB funciona de manera diferente a MySQL.

## 🟢 En MySQL (Relacional)
- Se crean bases de datos manualmente.
- Se crean tablas con estructura fija.
- Se definen columnas obligatorias.
- Se usan relaciones con llaves foráneas (JOIN).

## 🟢 En MongoDB (NoSQL)
- La base de datos se crea automáticamente al insertar el primer documento.
- Las colecciones se crean automáticamente cuando se insertan datos.
- No existen tablas, existen colecciones.
- No existen filas, existen documentos (JSON).
- No se usan JOIN tradicionales.
- La estructura es flexible (documentos pueden variar).

⚠️ Importante:
No debemos crear manualmente las colecciones en Atlas.
Las colecciones se crean desde el código cuando insertamos datos usando FastAPI.


