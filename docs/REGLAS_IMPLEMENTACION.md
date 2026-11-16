# Reglas de implementación — Plataforma DDRR–Catastro

Plataforma web con asistente de IA para revisar documentos de registro de bienes raíces en Derechos Reales (DDRR) y Catastro, Cochabamba.

Este documento es de cumplimiento obligatorio para todo el equipo. Define la arquitectura, el stack congelado, las reglas de código y la lista de tareas por fases.

---

## 1. Decisiones congeladas

### 1.1 Arquitectura

- **Monolito modular:** una sola API FastAPI organizada en módulos.
- **Un único proceso adicional:** el worker de IA (ARQ), que consume jobs desde Redis.
- Quedan descartados: microservicios y API Gateway.

### 1.2 Stack (no se cambia durante todo el proyecto)

| Capa | Tecnología fija |
|---|---|
| Lenguaje backend | Python (versión estable más reciente al iniciar, fijada en `.python-version`) |
| Gestor de dependencias | uv |
| Framework API | FastAPI + Pydantic v2 |
| ORM y migraciones | SQLAlchemy 2 + GeoAlchemy2 + Alembic |
| Base de datos | PostgreSQL + PostGIS (en Docker) |
| Cola y caché | Redis (en Docker) + ARQ |
| IA | Ollama (local, instalado en el equipo) con el paquete oficial `ollama` de Python |
| Lectura de PDFs | PyMuPDF (texto) + Tesseract con idioma español (escaneados) |
| Archivos | Disco local, carpeta `storage/` |
| Contraseñas | pwdlib (argon2) |
| Tokens | PyJWT |
| Biometría | WebAuthn: `py_webauthn` (backend) y `@simplewebauthn/browser` (frontend) |
| QR y firma | `segno` + `cryptography` (firma Ed25519) |
| Pruebas backend | pytest + httpx |
| Calidad backend | Ruff |
| Frontend | React + TypeScript + Vite + Tailwind CSS |
| Frontend: rutas y datos | React Router + TanStack Query |
| Frontend: formularios | React Hook Form + Zod |
| Frontend: visor y gráficos | react-pdf (pdf.js) + Recharts |
| Frontend: inactividad | react-idle-timer |
| Pruebas y calidad frontend | Vitest + ESLint + Prettier |
| Infraestructura | Docker Compose |
| Control de versiones | Git |

### 1.3 Fuera de alcance de esta etapa

- Quechua y Aymara en el asistente (solo español).
- MinIO u otro almacén de objetos.
- Integración con los sistemas reales de DDRR y Catastro: se trabaja con datos simulados en la base propia.
- Despliegue en producción.

---

## 2. Reglas

### 2.1 Stack

- **R-STK-1.** Está prohibido cambiar, reemplazar o añadir una tecnología alternativa a cualquiera de la tabla 1.2, sin excepciones.
- **R-STK-2.** Ante un problema técnico, se resuelve dentro del stack. No se cambia de tecnología porque sea difícil.
- **R-STK-3.** Se permite una librería pequeña de apoyo solo si no reemplaza ni duplica una tecnología de la tabla. Se registra en `docs/dependencias.md` con nombre, motivo y fecha antes de instalarla.
- **R-STK-4.** Las versiones se fijan en `uv.lock` y `package-lock.json`. No se hacen actualizaciones de versión mayor durante el proyecto.
- **R-STK-5.** El modelo de Ollama se define en la variable `OLLAMA_MODEL`. Cambiar de modelo (dentro de Ollama) exige repetir la evaluación de la tarea T-5.8 y anotar el resultado en `docs/evaluacion-ia.md`.

### 2.2 Arquitectura

- **R-ARQ-1.** Cada módulo vive en `app/modules/<nombre>/` con los archivos `router.py`, `service.py`, `repository.py`, `models.py` y `schemas.py`.
- **R-ARQ-2.** Flujo permitido: `router → service → repository → models`. Ninguna capa salta a otra.
- **R-ARQ-3.** El `router` solo recibe y devuelve datos: no contiene reglas de negocio ni consultas.
- **R-ARQ-4.** El `service` contiene las reglas de negocio y las transacciones.
- **R-ARQ-5.** El `repository` es el único que habla con la base de datos.
- **R-ARQ-6.** Un módulo nunca importa el `repository` de otro módulo: usa su `service`.
- **R-ARQ-7.** Los esquemas Pydantic (`schemas.py`) están separados de los modelos ORM (`models.py`). Nunca se devuelve un modelo ORM directamente.
- **R-ARQ-8.** Toda acción que modifique datos importantes (documento, solicitud, usuario, certificación) pasa por el módulo de bitácora.

### 2.3 Código backend

- **R-BCK-1.** Todo el código lleva anotaciones de tipo y pasa `ruff check` y `ruff format` sin errores.
- **R-BCK-2.** Toda tabla usa clave primaria UUID y campos `created_at` y `updated_at` en UTC.
- **R-BCK-3.** Todo cambio en la base de datos se hace con una migración de Alembic. No se modifican tablas a mano.
- **R-BCK-4.** La configuración viene de variables de entorno (`.env`, no versionado). Se mantiene un `.env.example` sin secretos.
- **R-BCK-5.** Los errores se devuelven con un formato único: `{ "code": "...", "message": "..." }` y el código HTTP correcto.
- **R-BCK-6.** Las rutas llevan el prefijo `/api/v1`.
- **R-BCK-7.** Las coordenadas se almacenan en SRID 4326. La proyección métrica local se define en la tarea T-4.1.
- **R-BCK-8.** Las listas devueltas por la API usan paginación.

### 2.4 Seguridad

- **R-SEG-1.** Dos roles: `funcionario` y `encargado`. Cada endpoint declara el rol que exige.
- **R-SEG-2.** Acceso: usuario y contraseña, más verificación biométrica (WebAuthn) obligatoria para ambos roles.
- **R-SEG-3.** Token de acceso de vida corta (15 minutos). El refresh token va en cookie `httpOnly`, `Secure` y `SameSite`.
- **R-SEG-4.** Cierre automático por inactividad (10 minutos, configurable). Se aplica en el frontend y se verifica también en el servidor.
- **R-SEG-5.** Los tokens nunca se guardan en `localStorage` ni `sessionStorage`.
- **R-SEG-6.** Límite de intentos de login por usuario e IP. Las contraseñas se guardan solo con argon2.
- **R-SEG-7.** Solo se aceptan PDFs: se valida el tipo real del archivo (no solo la extensión) y un tamaño máximo configurable.
- **R-SEG-8.** Cada documento guarda su hash SHA-256 al subirse. Si el hash cambia, el documento se considera alterado.
- **R-SEG-9.** No se escriben datos personales, contraseñas ni tokens en los logs.
- **R-SEG-10.** El QR contiene solo una URL con el identificador del documento y su firma. Nunca datos personales.
- **R-SEG-11.** CORS limitado al origen del frontend. Ningún secreto se sube al repositorio.

### 2.5 IA con Ollama

- **R-IA-1.** La IA solo recomienda. Nunca escribe ni modifica datos de DDRR o Catastro.
- **R-IA-2.** Todo cambio que afecte datos de DDRR requiere una solicitud y la aprobación del encargado (módulo `modificaciones`).
- **R-IA-3.** Los datos de los documentos no salen del equipo ni del servidor: solo se usa Ollama local, sin servicios externos de IA.
- **R-IA-4.** El acceso al modelo está encapsulado en `app/ai/ollama_client.py`. Ningún módulo llama a Ollama directamente.
- **R-IA-5.** La IA devuelve JSON con un esquema definido. La salida se valida con Pydantic antes de usarse.
- **R-IA-6.** Temperatura baja (entre 0 y 0.2). Los prompts viven en `app/ai/prompts/`, versionados en Git.
- **R-IA-7.** El análisis corre siempre en el worker ARQ, nunca dentro de una petición HTTP.
- **R-IA-8.** Si la salida es inválida se reintenta hasta 2 veces. Si sigue fallando, el documento pasa a "revisión manual" y se avisa al funcionario.
- **R-IA-9.** Cada resultado guarda el modelo, la versión del prompt y la fecha, para poder auditarlo.
- **R-IA-10.** Las discrepancias se presentan como alertas con el campo, el valor encontrado en cada documento y el motivo. La decisión final es siempre humana.

### 2.6 Frontend

- **R-FRT-1.** TypeScript en modo `strict`. No se usa `any`.
- **R-FRT-2.** El frontend solo consume la API `/api/v1`. No accede a la base de datos ni a Ollama.
- **R-FRT-3.** Las peticiones pasan por TanStack Query. Los formularios usan React Hook Form + Zod.
- **R-FRT-4.** Estilos solo con Tailwind. No se añade otra librería de componentes.
- **R-FRT-5.** Estructura por funcionalidad: `src/features/<nombre>/`. Los componentes compartidos van en `src/components/`.
- **R-FRT-6.** Las rutas se protegen según el rol del usuario.

### 2.7 Git y calidad

- **R-GIT-1.** Ramas: `main` (estable), `dev` (integración) y `feature/<tarea>`. No se hace push directo a `main` ni a `dev`.
- **R-GIT-2.** Commits en formato `tipo(módulo): mensaje` (por ejemplo `feat(documentos): subir pdf`).
- **R-GIT-3.** Todo cambio entra por Pull Request revisado por al menos otra persona del equipo.
- **R-GIT-4.** Mínimo de pruebas: `auth`, `modificaciones` y `certificacion` con pruebas de sus servicios y endpoints.
- **R-GIT-5.** Una tarea está terminada solo si cumple la definición de la sección 3.

---

## 3. Definición de terminado (DoD)

Una tarea se marca `[x]` solo si:

- [ ] Funciona y se probó manualmente.
- [ ] Tiene pruebas, si pertenece a un módulo con prueba obligatoria (R-GIT-4).
- [ ] Pasa Ruff (backend) y ESLint + Prettier (frontend).
- [ ] Si cambia la base de datos, incluye su migración.
- [ ] El Pull Request fue revisado y aprobado.
- [ ] Respeta todas las reglas de la sección 2.

---

## 4. Estructura del repositorio

```
ddrr-catastro/
├─ docker-compose.yml
├─ docs/                    reglas, dependencias, evaluación de IA
├─ storage/                 PDFs (no versionado)
├─ backend/
│  ├─ pyproject.toml / uv.lock / alembic/
│  └─ app/
│     ├─ main.py
│     ├─ core/              config, db, seguridad, errores, logging
│     ├─ ai/                ollama_client.py, schemas.py, prompts/
│     ├─ worker/            configuración y jobs de ARQ
│     └─ modules/
│        ├─ auth/
│        ├─ funcionarios/
│        ├─ documentos/
│        ├─ revisiones/
│        ├─ modificaciones/
│        ├─ certificacion/
│        ├─ alertas/
│        ├─ bitacora/
│        └─ ddrr_catastro/
└─ frontend/
   └─ src/ { app, features, components, lib }
```

---

## 5. Lista de tareas

Marca cada tarea con `[x]` al cumplir la definición de terminado.

### Fase 0 — Entorno y cimientos

- [x] T-0.1 Crear el repositorio Git con las ramas `main` y `dev`, y el `.gitignore` (`.env`, `storage/`, `node_modules/`, `.venv/`).
- [x] T-0.2 Crear `docker-compose.yml` con PostgreSQL + PostGIS y Redis; verificar que levantan.
- [x] T-0.3 Instalar Ollama en el equipo, descargar un modelo de prueba y verificar una respuesta desde la terminal.
- [x] T-0.4 Instalar Tesseract con el idioma español y verificar que lee un PDF escaneado de ejemplo.
- [x] T-0.5 Inicializar el backend con uv, instalar las dependencias del stack y crear la estructura de carpetas.
- [x] T-0.6 Configurar Ruff y crear `.env.example` y `core/config.py`.
- [x] T-0.7 Crear la aplicación FastAPI con el endpoint `GET /api/v1/health`.
- [x] T-0.8 Inicializar Alembic y conectar con la base de datos.
- [x] T-0.9 Inicializar el frontend (Vite + React + TypeScript + Tailwind) y configurar ESLint y Prettier.
- [x] T-0.10 Crear `docs/dependencias.md` y copiar este documento en `docs/`.

### Fase 1 — Base del backend

- [x] T-1.1 Crear la clase base de modelos (UUID, `created_at`, `updated_at`).
- [x] T-1.2 Configurar la sesión de base de datos y la inyección de dependencias.
- [x] T-1.3 Implementar el manejador de errores con el formato único (R-BCK-5).
- [x] T-1.4 Configurar el logging sin datos sensibles (R-SEG-9).
- [x] T-1.5 Primera migración y prueba con pytest + httpx sobre `/health`.

### Fase 2 — Identidad, seguridad y funcionarios

- [x] T-2.1 Modelo y migración de usuarios con rol (`funcionario`, `encargado`).
- [x] T-2.2 Registro de contraseñas con argon2 y login con usuario y contraseña.
- [x] T-2.3 Emisión de token de acceso (15 min) y refresh en cookie `httpOnly`; endpoints de refresh y logout.
- [x] T-2.4 Dependencia de autorización por rol (R-SEG-1).
- [x] T-2.5 Registro y verificación de credencial WebAuthn en el backend.
- [x] T-2.6 Límite de intentos de login (R-SEG-6).
- [x] T-2.7 Control de inactividad en el servidor (R-SEG-4).
- [ ] T-2.8 Módulo `funcionarios`: crear, listar, ver, editar y eliminar (solo `encargado`).
- [x] T-2.9 Módulo `bitacora`: registro de acciones con usuario, fecha y hora; endpoint de consulta.
- [ ] T-2.10 Frontend: pantalla de login, paso WebAuthn, rutas protegidas por rol y cierre por inactividad con `react-idle-timer`.
- [ ] T-2.11 Pruebas del módulo `auth` (login, token, roles, intentos fallidos).

### Fase 3 — Documentos

- [ ] T-3.1 Modelo y migración de documentos (tipo, hash, ruta, estado, usuario).
- [ ] T-3.2 Subida de PDF con validación de tipo real y tamaño (R-SEG-7).
- [ ] T-3.3 Cálculo y almacenamiento del hash SHA-256 (R-SEG-8).
- [ ] T-3.4 Endpoints: listar, ver detalle y servir el PDF con control de acceso.
- [ ] T-3.5 Frontend: pantalla de subida y listado de documentos.
- [ ] T-3.6 Frontend: visor de PDF con `react-pdf`.

### Fase 4 — DDRR y Catastro (datos simulados)

- [ ] T-4.1 Definir el modelo de datos: partidas (DDRR) y predios (Catastro, con geometría PostGIS) y la proyección métrica local.
- [ ] T-4.2 Migraciones de las tablas y los índices espaciales.
- [ ] T-4.3 Script de datos simulados (seed) con casos coherentes y casos con discrepancias deliberadas.
- [ ] T-4.4 Módulo `ddrr_catastro`: consultar partida y predio por identificador.
- [ ] T-4.5 Pruebas de las consultas.

### Fase 5 — Revisión con IA (Ollama)

- [ ] T-5.1 Cliente `ollama_client.py` con tiempo límite, reintentos y salida en JSON.
- [ ] T-5.2 Extracción de texto de PDFs: PyMuPDF para PDFs con texto y Tesseract para escaneados.
- [ ] T-5.3 Esquemas Pydantic de la salida de la IA (campos extraídos y discrepancias).
- [ ] T-5.4 Primer prompt versionado en `app/ai/prompts/` para extraer campos clave.
- [ ] T-5.5 Lógica de comparación entre documentos, y contra datos de DDRR y Catastro.
- [ ] T-5.6 Configurar el worker ARQ y el job de análisis (R-IA-7).
- [ ] T-5.7 Módulo `revisiones`: iniciar revisión, consultar estado y resultado, listar.
- [ ] T-5.8 Evaluar el modelo con un conjunto de documentos de prueba (al menos 10, con y sin errores); anotar resultados en `docs/evaluacion-ia.md` y fijar `OLLAMA_MODEL`.
- [ ] T-5.9 Manejo de salida inválida y estado "revisión manual" (R-IA-8).
- [ ] T-5.10 Frontend: botón para enviar a revisión, estado y vista del resultado.

### Fase 6 — Alertas

- [ ] T-6.1 Módulo `alertas`: modelo, creación a partir de discrepancias, listar y marcar como leída.
- [ ] T-6.2 WebSocket autenticado para enviar alertas en tiempo real.
- [ ] T-6.3 Frontend: lista de alertas y recepción por WebSocket.

### Fase 7 — Modificaciones y permiso del encargado

- [ ] T-7.1 Módulo `modificaciones`: modelo de solicitud (documento, campo, valor propuesto, estado).
- [ ] T-7.2 Regla de negocio: clasificar si el cambio afecta datos de DDRR (R-IA-2).
- [ ] T-7.3 Endpoints: solicitar, listar pendientes, aprobar y rechazar (aprobar y rechazar solo `encargado`).
- [ ] T-7.4 Aplicar el cambio y registrar en bitácora, en una sola transacción.
- [ ] T-7.5 Notificar al encargado y al funcionario por alertas y WebSocket.
- [ ] T-7.6 Frontend: solicitud del funcionario y pantalla de aprobación del encargado.
- [ ] T-7.7 Pruebas del módulo `modificaciones`.

### Fase 8 — Certificación y QR

- [ ] T-8.1 Módulo `certificacion`: marcar documento como final cuando no queden discrepancias ni solicitudes pendientes.
- [ ] T-8.2 Generación de la clave de firma y firma del documento (Ed25519).
- [ ] T-8.3 Generación del QR con `segno` (R-SEG-10).
- [ ] T-8.4 Endpoint público `GET /api/v1/verificar/{id}` que recalcula el hash y confirma la validez.
- [ ] T-8.5 Frontend: vista del documento final con QR y página pública de verificación.
- [ ] T-8.6 Pruebas del módulo `certificacion` (documento válido, alterado y firma inválida).

### Fase 9 — Dashboard del encargado

- [ ] T-9.1 Endpoint de funcionarios conectados.
- [ ] T-9.2 Endpoint de resumen de alertas por estado y por documento.
- [ ] T-9.3 Frontend: dashboard con alertas, conectados, notificaciones de modificación y gráficos con Recharts.
- [ ] T-9.4 Frontend: gestión de funcionarios (crear y eliminar) y lista de registros con día y hora.

### Fase 10 — Cierre

- [ ] T-10.1 Revisión de seguridad con la lista de las reglas R-SEG.
- [ ] T-10.2 Prueba completa del flujo: subir, revisar, alertar, solicitar cambio, aprobar, certificar y verificar el QR.
- [ ] T-10.3 Completar `docs/` con instalación, variables de entorno y resultados de la evaluación de IA.
- [ ] T-10.4 Preparar la demostración con datos simulados.

---

## 6. Registro de decisiones

| Fecha | Decisión |
|---|---|
| 2026-11-06 | Arquitectura: monolito modular con worker de IA |
| 2026-11-06 | IA: Ollama local; sin servicios externos de IA |
| 2026-11-06 | Stack congelado según la sección 1.2 |
| 2026-11-06 | Fuera de alcance: quechua y aymara, MinIO, integración con sistemas reales |
