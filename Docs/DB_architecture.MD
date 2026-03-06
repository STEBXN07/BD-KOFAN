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

---

# Conexión a MongoDB

Este documento explica las formas de conexión utilizadas para acceder al clúster de base de datos en **MongoDB** y en qué situaciones se recomienda cada una.

---

# 1. Conexión SRV (Recomendada)

La conexión **SRV** es el método recomendado por MongoDB porque simplifica la configuración y gestiona automáticamente la información del clúster.

## Características

- Es la conexión recomendada por MongoDB.
- Detecta automáticamente los nodos del clúster.
- Requiere menos configuración manual.
- Más fácil de utilizar en aplicaciones modernas.

## Ejemplo de conexión

```bash
mongodb+srv://kofan_admin:Kofan2026@kofan-cluster.j9z4urw.mongodb.net/
```

## Cuándo usarla

Se recomienda usar esta conexión cuando:

- El entorno tiene resolución DNS funcionando correctamente.
- Se utilizan herramientas compatibles con SRV.
- Se desea una configuración más simple.

---

# 2. Conexión Estándar

La conexión estándar utiliza el protocolo `mongodb://` y especifica manualmente los nodos del clúster.

## Características

- No depende de registros DNS SRV.
- Permite definir manualmente cada nodo del clúster.
- Puede ser más estable en algunos entornos o herramientas.

## Ejemplo de conexión

```bash
mongodb://kofan_admin:Kofan2026@ac-ngcm4n8-shard-00-00.j9z4urw.mongodb.net:27017,ac-ngcm4n8-shard-00-01.j9z4urw.mongodb.net:27017,ac-ngcm4n8-shard-00-02.j9z4urw.mongodb.net:27017/?tls=true&authSource=admin&retryWrites=true&w=majority
```

## Cuándo usarla

Se recomienda usar esta conexión cuando:

- Existen problemas de resolución DNS.
- Algunas herramientas o entornos no soportan `mongodb+srv`.
- Se necesita mayor control sobre los nodos del clúster.

---

# Recomendación

Siempre que sea posible se debe utilizar la conexión **SRV**, ya que es el estándar recomendado por MongoDB.

Sin embargo, en caso de problemas de DNS o incompatibilidad con herramientas de desarrollo, la conexión **estándar** es una alternativa totalmente válida.

---


