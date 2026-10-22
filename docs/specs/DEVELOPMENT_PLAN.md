Hola, soy Developer. Mi función es implementar las funcionalidades del proyecto.

# DEVELOPMENT PLAN: Pre-screening para Ensayos Clínicos Estado 1

## 1. ARCHITECTURE OVERVIEW

El proyecto "Pre-screening para Ensayos Clínicos Estado 1" se implementará como un monolito modular utilizando un stack tecnológico que incluye React para el frontend, FastAPI con Python para el backend y PostgreSQL como base de datos. La arquitectura está diseñada para cumplir con las normativas de privacidad clínica (GDPR/HIPAA), asegurando la trazabilidad de las evaluaciones, el enmascaramiento y cifrado de PII, y un registro de auditoría inmutable.

**Componentes Principales:**

*   **Frontend (React/TypeScript):** Una interfaz de usuario responsive optimizada para tablets/iPads, que sigue fielmente el contrato de diseño UI/UX. Incluye páginas para acceso seguro, centro de evaluaciones, formulario de evaluación clínica, resolución de elegibilidad, auditoría y trazabilidad, y un panel de reclutamiento. Utiliza Tailwind CSS con tokens de diseño específicos y componentes reutilizables.
*   **Backend (FastAPI/Python):** Una API RESTful que expone endpoints para autenticación, gestión de pacientes, protocolos, evaluaciones, reglas de evaluación, logs de auditoría y métricas. Incorpora un motor de reglas booleano para el protocolo ALM-PSO-2026, validación de datos con Pydantic, autenticación JWT y autorización basada en roles. Los datos PII se cifran antes de ser almacenados en la base de datos.
*   **Base de Datos (PostgreSQL):** Persistencia de datos para usuarios, pacientes, protocolos, criterios, evaluaciones, reglas de evaluación y logs de auditoría. El esquema se gestiona con SQLAlchemy ORM y se inicializa automáticamente al inicio del servicio. Se implementa un mecanismo de hash encadenado para garantizar la inmutabilidad del registro de auditoría.
*   **Motor de Reglas:** Un módulo dedicado en el backend que implementa la lógica booleana para evaluar la elegibilidad de los pacientes según los criterios del protocolo ALM-PSO-2026, con latencia cercana a cero.
*   **Contenerización (Docker y Docker Compose):** Todos los servicios (frontend, backend, base de datos) se empaquetarán en contenedores Docker y se orquestarán con Docker Compose para facilitar el desarrollo local y el despliegue en entornos de staging y producción.

**Modelos de Datos Clave:**

*   **USUARIO:** Almacena información de usuarios con roles (`investigador`, `gestor`).
*   **PACIENTE:** Contiene datos del paciente, incluyendo PII enmascarados/cifrados (`codigo_interno`, `seudonimo`, `datos_clinicos`).
*   **PROTOCOLO:** Define los protocolos clínicos.
*   **CRITERIO:** Criterios de inclusión/exclusión asociados a un protocolo.
*   **EVALUACION:** Registra cada evaluación de un paciente por un investigador bajo un protocolo.
*   **REGLA_EVALUACION:** Detalle de cómo cada criterio fue evaluado para una evaluación específica.
*   **AUDIT_LOG:** Registro inmutable de auditoría con hash encadenado para trazabilidad GxP.

**Estructura de Carpetas:**

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── pacientes.py
│   │   │   │   ├── protocolos.py
│   │   │   │   ├── criterios.py
│   │   │   │   ├── evaluaciones.py
│   │   │   │   ├── reglas_evaluacion.py
│   │   │   │   ├── audit_logs.py
│   │   │   │   └── metrics.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── exceptions.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── patient_service.py
│   │   │   ├── protocol_service.py
│   │   │   ├── evaluation_service.py
│   │   │   ├── audit_service.py
│   │   │   └── metrics_service.py
│   │   └── rules_engine/
│   │       ├── __init__.py
│   │       └── protocol_alm_pso_2026.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── session.py
│   │   └── crud.py
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   ├── dependencies.py
│   │   └── utils.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   ├── api/
│   │   │   ├── auth.ts
│   │   │   ├── patients.ts
│   │   │   ├── protocols.ts
│   │   │   ├── evaluations.ts
│   │   │   ├── auditLogs.ts
│   │   │   └── metrics.ts
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   │   ├── AppShell.tsx
│   │   │   │   ├── PrimaryButton.tsx
│   │   │   │   ├── ClinicalCard.tsx
│   │   │   │   ├── StatusPill.tsx
│   │   │   │   ├── CriterionRow.tsx
│   │   │   │   ├── ClinicalField.tsx
│   │   │   │   ├── DataTable.tsx
│   │   │   │   └── StatCard.tsx
│   │   │   └── common/
│   │   │       ├── LoadingSpinner.tsx
│   │   │       └── ErrorMessage.tsx
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── usePatients.ts
│   │   │   ├── useEvaluations.ts
│   │   │   ├── useAuditLogs.ts
│   │   │   └── useMetrics.ts
│   │   ├── pages/
│   │   │   ├── AccesoSeguro.tsx
│   │   │   ├── CentroDeEvaluaciones.tsx
│   │   │   ├── FormularioDeEvaluacionClinica.tsx
│   │   │   ├── ResolucionDeElegibilidad.tsx
│   │   │   ├── AuditoriaYTrazabilidad.tsx
│   │   │   └── PanelDeReclutamiento.tsx
│   │   ├── styles/
│   │   │   ├── tokens.ts
│   │   │   └── tailwind.css
│   │   └── types/
│   │       ├── api.ts
│   │       └── common.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── .dockerignore
├── run.sh
└── README.md
```

## 2. ACCEPTANCE CRITERIA
1.  El sistema debe indicar claramente los campos obligatorios y prevenir el envío del formulario hasta que todos estén completados.
2.  El sistema debe mostrar mensajes de error específicos para cada campo con valores fuera de rango. La edad se valida como número entero entre 0 y 120. PASI y BSA se validan como números entre 0 y 100.
3.  Al pulsar evaluar, se muestra un indicador de carga. Si la API responde correctamente, el panel muestra el estado 'Elegible'. El desglose de criterios indica que el paciente cumple todos los criterios de inclusión y ninguno de exclusión.
4.  Al pulsar evaluar, se muestra un indicador de carga. Si la API responde correctamente, el panel muestra el estado 'No Elegible'. El desglose de criterios indica que el paciente falla al menos un criterio de inclusión (por ejemplo, edad < 18).
5.  Al pulsar evaluar, se muestra un indicador de carga. Si la API responde correctamente, el panel muestra el estado 'No Elegible'. El desglose de criterios indica que el paciente presenta al menos un criterio de exclusión (por ejemplo, historial de tuberculosis).
6.  Los campos PII se muestran enmascarados en la interfaz antes del veredicto del pre-screening.
7.  Cada evaluación registra usuario, fecha/hora, identificador seudonimizado del paciente, resultado y criterios fallados. Los registros de trazabilidad no almacenan PII sin enmascarar. El gestor puede consultar un panel con los registros de auditoría.
8.  Al pulsar evaluar, se muestra un indicador de carga. Si la API responde correctamente, el panel muestra el estado 'No Elegible'. El desglose de criterios indica que el paciente falla el criterio PASI >= 10.
9.  Al pulsar evaluar, se muestra un indicador de carga. Si la API responde correctamente, el panel muestra el estado 'Elegible'. El desglose de criterios indica que el paciente cumple el criterio de diagnóstico de Psoriasis crónica >= 6 meses.
10. Al pulsar evaluar, se muestra un indicador de carga. Si la API responde correctamente, el panel muestra el estado 'Elegible'. El desglose de criterios indica que el paciente no presenta el criterio de exclusión 'uso de biológicos/corticoides recientes'.
11. El backend debe validar estrictamente los esquemas de entrada (con Pydantic) y rechazar la petición con un error, evitando que comprometa la base de datos PostgreSQL.
12. El frontend en React debe bloquear la introducción de fechas ilógicas o valores analíticos imposibles antes de enviar la petición asíncrona al backend, mostrando un mensaje de error claro al usuario.
13. Cada evaluación registra obligatoriamente la identidad del investigador (vía token JWT), la marca de tiempo y el veredicto exacto. Los registros de trazabilidad no almacenan PII sin enmascarar.
14. El gestor puede consultar un panel con totales de elegibles/no elegibles. Los datos deben reflejar las evaluaciones realizadas.
15. Los campos PII se muestran enmascarados en la interfaz después de emitir el veredicto del paciente.
16. El formulario muestra todos los campos definidos en el protocolo ALM-PSO-2026.
17. Al pulsar evaluar, se muestra un indicador de carga. Si la API responde correctamente, el panel muestra el estado 'No Elegible'. El desglose de criterios indica que el paciente falla múltiples criterios de inclusión (por ejemplo, edad y PASI).
18. Al pulsar evaluar, se muestra un indicador de carga. Si la API responde correctamente, el panel muestra el estado 'No Elegible'. El desglose de criterios indica que el paciente presenta múltiples criterios de exclusión (por ejemplo, embarazo e historial de TB).
19. Al pulsar evaluar, se muestra un indicador de carga. Si la API responde con un error, el frontend debe mostrar un mensaje de error amigable al usuario y no redirigir al panel de resolución, permitiendo reintentar o revisar los datos.
20. La base de datos debe bloquear alteraciones de registros pasados para el audit trail, manteniendo su inmutabilidad. La operación de modificación debe fallar.
21. El sistema debe aceptar todos los valores ingresados en los límites de los rangos definidos (Edad entre 0 y 120, PASI entre 0 y 100, BSA entre 0 y 100) sin mostrar mensajes de error.
22. El tiempo de evaluación por paciente debe ser inferior a 2 minutos, con una latencia percibida cercana a cero en la lógica booleana del protocolo médico.
23. La lógica booleana del protocolo médico responde con latencia cercana a cero (milisegundos) para determinar la elegibilidad.
24. El tiempo de evaluación por paciente se reduce a menos de 2 minutos.
25. Los campos de identificación personal (PII) se muestran enmascarados en la interfaz antes de mostrar el veredicto del pre-screen.
26. Los registros de trazabilidad no almacenan PII sin enmascarar, utilizando identificadores seudonimizados para el paciente.
27. El log inmutable de las reglas de rechazo (Audit Trail) no permite modificaciones ni eliminaciones, asegurando el 100% de cumplimiento del audit trail para pacientes rechazados.
28. La interfaz de usuario React se adapta y es completamente funcional y ergonómica en tablets/iPads, permitiendo una interacción fluida.
29. El sistema mantiene tiempos de respuesta consistentes y un rendimiento estable para 2-3 usuarios concurrentes, sin degradación significativa en el tiempo de evaluación por paciente.
30. La base de datos se restaura exitosamente a su estado previo al incidente, conservando todos los datos de pacientes y los registros de auditoría intactos.
31. El backend debe validar estrictamente los esquemas de entrada (con Pydantic) y rechazar la petición con un error de validación, sin comprometer la base de datos PostgreSQL.
32. El frontend en React debe bloquear la introducción de fechas ilógicas o valores analíticos imposibles, mostrando un mensaje de error claro al usuario, antes de enviar la petición asíncrona al backend.
33. Cada evaluación registra obligatoriamente la identidad del investigador (vía token JWT), la marca de tiempo y el veredicto exacto.
34. La base de datos debe bloquear alteraciones de registros pasados de pacientes. El borrado lógico (soft delete) debe funcionar, marcando el registro como inactivo pero manteniéndolo en la base de datos y en el audit trail.
35. Cada evaluación registra usuario, fecha/hora, identificador seudonimizado del paciente, resultado y criterios fallados, independientemente del veredicto.
36. El sistema se despliega correctamente y es completamente funcional en el entorno de staging, permitiendo a los investigadores usarlo sin problemas.
37. Los endpoints de la API están diseñados con recursos FHIR básicos para prever escalabilidad futura, aunque sin integraciones reales en esta fase.
38. Los campos de identificación personal (PII) deben estar cifrados en la base de datos para cumplir con las normativas de privacidad clínica (GDPR/HIPAA).
39. La base de datos se recupera a un estado operativo y consistente en un tiempo razonable, con todos los datos de pacientes y el audit trail intactos, según la estrategia de restauración rápida.
40. La API debe rechazar el acceso a endpoints sensibles (ej. /api/v1/evaluate) sin un token JWT válido, devolviendo un error de autenticación (ej. 401 Unauthorized). La identidad del investigador debe ser registrada en el audit trail.

## 3. EXECUTABLE ITEMS

### ITEM 1: Foundation — Shared Schemas, DB Models, Config, Core Utilities & UI Components
**Goal:** Crear toda la infraestructura compartida y los componentes base que serán importados por otros ítems. Esto incluye los modelos de datos Pydantic y SQLAlchemy, la configuración de la aplicación, utilidades de seguridad y PII, la gestión de sesiones de base de datos, y los componentes UI fundamentales y estilos globales.
**Files to create:**
- backend/app/__init__.py (create)
- backend/app/api/__init__.py (create)
- backend/app/api/v1/__init__.py (create)
- backend/app/core/__init__.py (create)
- backend/app/core/config.py (create) - Configuración de la aplicación y variables de entorno.
- backend/app/core/security.py (create) - Funciones para JWT, hashing de contraseñas.
- backend/app/core/exceptions.py (create) - Manejadores de excepciones personalizados.
- backend/app/services/__init__.py (create)
- backend/app/rules_engine/__init__.py (create)
- backend/database/__init__.py (create)
- backend/database/models.py (create) - Definición de todos los modelos SQLAlchemy ORM.
- backend/database/session.py (create) - Gestión de la sesión de la base de datos.
- backend/database/crud.py (create) - Operaciones CRUD genéricas para los modelos.
- backend/shared/__init__.py (create)
- backend/shared/schemas.py (create) - Definición de todos los modelos Pydantic para la API.
- backend/shared/dependencies.py (create) - Dependencias de FastAPI para autenticación y roles.
- backend/shared/utils.py (create) - Utilidades para enmascaramiento de PII y hash encadenado.
- backend/requirements.txt (create) - Todas las dependencias de Python.
- frontend/public/index.html (create) - Archivo HTML principal.
- frontend/src/main.tsx (create) - Punto de entrada de la aplicación React.
- frontend/src/App.tsx (create) - Componente principal de la aplicación y enrutamiento.
- frontend/src/index.css (create) - Estilos globales.
- frontend/src/styles/tokens.ts (create) - Definición de los tokens de diseño.
- frontend/src/styles/tailwind.css (create) - Directivas de Tailwind CSS.
- frontend/src/types/api.ts (create) - Interfaces TypeScript para los contratos de datos de la API.
- frontend/src/types/common.ts (create) - Tipos comunes de utilidad.
- frontend/src/components/ui/AppShell.tsx (create) - Estructura base responsive con navegación.
- frontend/src/components/ui/PrimaryButton.tsx (create) - Botón de acción principal.
- frontend/src/components/ui/ClinicalCard.tsx (create) - Contenedor para secciones clínicas.
- frontend/src/components/ui/StatusPill.tsx (create) - Etiqueta semántica para estado/elegibilidad.
- frontend/src/components/ui/CriterionRow.tsx (create) - Muestra un criterio y su estado.
- frontend/src/components/ui/ClinicalField.tsx (create) - Campo de entrada para datos clínicos.
- frontend/src/components/ui/DataTable.tsx (create) - Componente genérico de tabla.
- frontend/src/components/ui/StatCard.tsx (create) - Tarjeta para mostrar estadísticas.
- frontend/src/components/common/LoadingSpinner.tsx (create) - Spinner de carga genérico.
- frontend/src/components/common/ErrorMessage.tsx (create) - Mensaje de error genérico.
- frontend/package.json (create) - Dependencias y scripts de frontend.
- frontend/tsconfig.json (create) - Configuración de TypeScript para frontend.
- frontend/vite.config.ts (create) - Configuración de Vite.
- frontend/nginx.conf (create) - Configuración de Nginx para servir la aplicación React.
**Dependencies:** None
**Validation:**
1.  Verificar que todos los archivos Python y TypeScript se compilan sin errores.
2.  Ejecutar un script Python para verificar la conexión a la base de datos y la creación de tablas a través de SQLAlchemy.
3.  Verificar que los tokens de diseño se exportan correctamente desde `frontend/src/styles/tokens.ts`.
4.  Verificar que los componentes UI básicos (`AppShell`, `PrimaryButton`, `ClinicalField`) se renderizan correctamente en un entorno de prueba local.
**Role:** role-tl (technical_lead)

### ITEM 2: Backend — Authentication & User Management
**Goal:** Implementar los endpoints de autenticación de usuarios y la gestión de perfiles de usuario. Esto incluye el login de usuarios y la recuperación de la información del usuario autenticado.
**Files to create:**
- backend/app/main.py (create) - Punto de entrada de la aplicación FastAPI, incluye eventos de lifespan para inicialización de DB y seeding.
- backend/app/api/v1/auth.py (create) - Endpoints para `POST /auth/login`.
- backend/app/api/v1/users.py (create) - Endpoints para `GET /users/me`.
- backend/app/services/auth_service.py (create) - Lógica de negocio para autenticación.
- backend/Dockerfile (create) - Dockerfile para el servicio backend (build context: ./backend) — CMD: uvicorn app.main:app --host 0.0.0.0 --port 21001
**Dependencies:** Item 1
**Validation:**
1.  Iniciar el backend y verificar que el endpoint `/health` (implícito en estándares empresariales) responde correctamente.
2.  Enviar una petición `POST` a `/auth/login` con credenciales válidas y verificar que se recibe un token JWT.
3.  Enviar una petición `GET` a `/users/me` con un token JWT válido y verificar que se devuelve la información del usuario.
4.  Verificar que el backend rechaza peticiones sin JWT o con JWT inválido para `/users/me`.
**Role:** role-be (backend_developer)

### ITEM 3: Backend — Patient & Protocol Management
**Goal:** Desarrollar los endpoints para la gestión de pacientes (CRUD) y la consulta de protocolos clínicos y sus criterios asociados. Se incluirá la lógica de cifrado/descifrado de PII para el almacenamiento en la base de datos.
**Files to create:**
- backend/app/api/v1/pacientes.py (create) - Endpoints para `POST /pacientes`, `GET /pacientes/{paciente_id}`, `PUT /pacientes/{paciente_id}`.
- backend/app/api/v1/protocolos.py (create) - Endpoints para `GET /protocolos`, `GET /protocolos/{protocolo_id}`.
- backend/app/api/v1/criterios.py (create) - Endpoints para `GET /protocolos/{protocolo_id}/criterios`.
- backend/app/services/patient_service.py (create) - Lógica de negocio para operaciones con pacientes, incluyendo cifrado/descifrado de PII.
- backend/app/services/protocol_service.py (create) - Lógica de negocio para operaciones con protocolos y criterios.
**Dependencies:** Item 1
**Validation:**
1.  Crear un paciente vía `POST /pacientes` y verificar que los campos PII se almacenan cifrados en la base de datos.
2.  Recuperar un paciente vía `GET /pacientes/{paciente_id}` y verificar que los campos PII se descifran correctamente para la respuesta.
3.  Listar protocolos y criterios asociados a un protocolo específico.
4.  Verificar que los endpoints requieren autenticación JWT y autorización por rol (`investigador`/`gestor`).
**Role:** role-be (backend_developer)

### ITEM 4: Backend — Evaluation & Rule Engine
**Goal:** Implementar la lógica del motor de reglas para el protocolo ALM-PSO-2026 y los endpoints para iniciar y someter evaluaciones de pacientes.
**Files to create:**
- backend/app/api/v1/evaluaciones.py (create) - Endpoints para `POST /evaluaciones`, `GET /evaluaciones`, `GET /evaluaciones/{evaluacion_id}`, `POST /evaluaciones/{evaluacion_id}/submit`.
- backend/app/rules_engine/protocol_alm_pso_2026.py (create) - Definición de reglas y lógica de evaluación para el protocolo ALM-PSO-2026.
- backend/app/services/evaluation_service.py (create) - Lógica de negocio para el flujo de evaluación, integración con el motor de reglas y registro de resultados.
**Dependencies:** Item 1
**Validation:**
1.  Iniciar una evaluación para un paciente y protocolo específicos.
2.  Someter datos clínicos para una evaluación y verificar que el motor de reglas determina correctamente la elegibilidad (`elegible`/`noElegible`).
3.  Verificar que la evaluación registra el `usuario_id` del investigador.
4.  Probar casos límite para PASI, BSA, edad y duración de psoriasis crónica, verificando que el resultado de la evaluación es el esperado (TC008, TC009, TC010).
5.  Verificar que el backend valida los datos de entrada (`EvaluacionSubmitData`) con Pydantic (TC011, NFR009).
**Role:** role-be (backend_developer)

### ITEM 5: Backend — Audit Logs & Metrics
**Goal:** Desarrollar los endpoints para consultar los registros de auditoría y las métricas agregadas de las evaluaciones.
**Files to create:**
- backend/app/api/v1/audit_logs.py (create) - Endpoints para `GET /audit-logs`.
- backend/app/api/v1/metrics.py (create) - Endpoints para `GET /metrics/evaluaciones`.
- backend/app/api/v1/reglas_evaluacion.py (create) - Endpoints para `GET /evaluaciones/{evaluacion_id}/reglas`.
- backend/app/services/audit_service.py (create) - Lógica de negocio para el registro y consulta de auditoría, incluyendo el hash encadenado.
- backend/app/services/metrics_service.py (create) - Lógica de negocio para el cálculo de métricas de evaluación.
**Dependencies:** Item 1
**Validation:**
1.  Realizar varias evaluaciones (elegibles y no elegibles) y verificar que se generan registros de auditoría inmutables con hash encadenado.
2.  Consultar los logs de auditoría y verificar que no contienen PII sin enmascarar.
3.  Consultar las métricas de evaluación y verificar que los totales de elegibles/no elegibles y los motivos de rechazo son correctos.
4.  Verificar que los endpoints de auditoría y métricas requieren el rol de `gestor`.
**Role:** role-be (backend_developer)

### ITEM 6: Frontend — Authentication Flow (Acceso Seguro)
**Goal:** Implementar la página de inicio de sesión (`AccesoSeguro.tsx`) y el hook de autenticación (`useAuth.ts`) para gestionar el estado de autenticación del usuario.
**Files to create:**
- frontend/src/pages/AccesoSeguro.tsx (create) - Página de inicio de sesión.
- frontend/src/api/auth.ts (create) - Cliente API para endpoints de autenticación.
- frontend/src/hooks/useAuth.ts (create) - Hook para la gestión del estado de autenticación.
**Dependencies:** Item 1
**Validation:**
1.  Acceder a la ruta de login y verificar que el formulario se renderiza correctamente.
2.  Intentar iniciar sesión con credenciales válidas y verificar que el usuario es redirigido a la página principal y el estado de autenticación se actualiza.
3.  Intentar iniciar sesión con credenciales inválidas y verificar que se muestra un mensaje de error amigable.
4.  Verificar que los campos PII (email) se enmascaran en la interfaz si aplica (TC006, NFR003).
**Role:** role-fe (frontend_developer)

### ITEM 7: Frontend — Dashboard & Patient List (Centro de Evaluaciones)
**Goal:** Implementar la página principal del "Centro de Evaluaciones" (`CentroDeEvaluaciones.tsx`) que muestra un listado de pacientes y evaluaciones recientes.
**Files to create:**
- frontend/src/pages/CentroDeEvaluaciones.tsx (create) - Dashboard principal con listado de evaluaciones.
- frontend/src/api/patients.ts (create) - Cliente API para endpoints de pacientes.
- frontend/src/api/evaluations.ts (create) - Cliente API para endpoints de evaluaciones.
- frontend/src/hooks/usePatients.ts (create) - Hook para la gestión de datos de pacientes.
- frontend/src/hooks/useEvaluations.ts (create) - Hook para la gestión de datos de evaluaciones.
**Dependencies:** Item 1, Item 3, Item 4, Item 6
**Validation:**
1.  Navegar a la página "Centro de Evaluaciones" y verificar que se muestra una tabla con evaluaciones recientes.
2.  Verificar que la tabla de evaluaciones muestra los datos de pacientes con PII enmascarados.
3.  Verificar que la interfaz es responsive en diferentes tamaños de pantalla (NFR006).
4.  Verificar que los datos se cargan desde el backend y se manejan los estados de carga y error.
**Role:** role-fe (frontend_developer)

### ITEM 8: Frontend — Clinical Evaluation Form (Formulario de Evaluación Clínica)
**Goal:** Implementar el "Formulario de Evaluación Clínica" (`FormularioDeEvaluacionClinica.tsx`) para que los investigadores ingresen los parámetros clínicos del paciente.
**Files to create:**
- frontend/src/pages/FormularioDeEvaluacionClinica.tsx (create) - Formulario para ingresar datos clínicos del paciente.
- frontend/src/api/protocols.ts (create) - Cliente API para endpoints de protocolos.
**Dependencies:** Item 1, Item 3, Item 4, Item 7
**Validation:**
1.  Acceder al formulario de evaluación y verificar que se muestran todos los campos definidos en el protocolo ALM-PSO-2026 (TC016).
2.  Verificar que los campos obligatorios se indican claramente y el envío está deshabilitado si no están completos (TC001).
3.  Ingresar valores fuera de rango para Edad, PASI y BSA y verificar que se muestran mensajes de error específicos (TC002, TC012, NFR010).
4.  Ingresar valores en los límites permitidos y verificar que no se muestran errores (TC021).
5.  Enviar el formulario con datos válidos y verificar que se muestra un indicador de carga y la petición se envía al backend.
6.  Verificar que los campos PII se muestran enmascarados en la interfaz (TC006, NFR003).
**Role:** role-fe (frontend_developer)

### ITEM 9: Frontend — Eligibility Resolution (Resolución de Elegibilidad)
**Goal:** Implementar la página de "Resolución de Elegibilidad" (`ResolucionDeElegibilidad.tsx`) que muestra el veredicto de la evaluación y el desglose de criterios.
**Files to create:**
- frontend/src/pages/ResolucionDeElegibilidad.tsx (create) - Página que muestra el resultado de la evaluación y el desglose de criterios.
- frontend/src/hooks/useEvaluationDetails.ts (create) - Hook para obtener detalles de una evaluación y sus reglas.
**Dependencies:** Item 1, Item 4, Item 7, Item 8
**Validation:**
1.  Después de someter una evaluación, verificar que se redirige a esta página y se muestra el estado 'Elegible' o 'No Elegible' con color, texto e icono (TC003, TC004, TC005).
2.  Verificar que se muestra el desglose de criterios, indicando cuáles se cumplen y cuáles no.
3.  Probar con diferentes escenarios de elegibilidad/no elegibilidad (fallo de inclusión, cumplimiento de exclusión, múltiples fallos) y verificar la visualización correcta.
4.  Verificar que los campos PII se muestran enmascarados en la interfaz (TC015, NFR003).
5.  Simular un error de la API al someter la evaluación y verificar que el frontend muestra un mensaje amigable y no redirige (TC019).
**Role:** role-fe (frontend_developer)

### ITEM 10: Frontend — Audit & Recruitment Panels (Auditoría y Trazabilidad, Panel de Reclutamiento)
**Goal:** Implementar las páginas para la "Auditoría y Trazabilidad" (`AuditoriaYTrazabilidad.tsx`) y el "Panel de Reclutamiento" (`PanelDeReclutamiento.tsx`).
**Files to create:**
- frontend/src/pages/AuditoriaYTrazabilidad.tsx (create) - Página para consultar los registros de auditoría.
- frontend/src/pages/PanelDeReclutamiento.tsx (create) - Dashboard con estadísticas de reclutamiento.
- frontend/src/api/auditLogs.ts (create) - Cliente API para endpoints de logs de auditoría.
- frontend/src/api/metrics.ts (create) - Cliente API para endpoints de métricas.
- frontend/src/hooks/useAuditLogs.ts (create) - Hook para la gestión de logs de auditoría.
- frontend/src/hooks/useMetrics.ts (create) - Hook para la gestión de métricas.
**Dependencies:** Item 1, Item 5, Item 7
**Validation:**
1.  Acceder a la página "Auditoría y Trazabilidad" (con rol `gestor`) y verificar que se muestra una tabla con los registros de auditoría.
2.  Verificar que los registros de auditoría muestran la información relevante (usuario, fecha, resultado, criterios fallados) y no PII sin enmascarar.
3.  Acceder a la página "Panel de Reclutamiento" (con rol `gestor`) y verificar que se muestran las estadísticas agregadas de elegibles/no elegibles y motivos de rechazo (TC014).
4.  Verificar que ambas páginas son responsive y los datos se cargan correctamente desde el backend.
**Role:** role-fe (frontend_developer)

### ITEM 11: Infrastructure & Deployment
**Goal:** Completar la orquestación Docker para que el proyecto se pueda construir y ejecutar con un solo comando (`./run.sh`), incluyendo la configuración de variables de entorno, healthchecks y documentación.
**Files to create:**
- docker-compose.yml (create) - Configuración de Docker Compose para todos los servicios (frontend, backend, db) con healthchecks y `depends_on`.
- .env.example (create) - Archivo de ejemplo con todas las variables de entorno requeridas y sus descripciones.
- .gitignore (create) - Archivo para ignorar directorios y archivos generados.
- .dockerignore (create) - Archivo para ignorar archivos durante la construcción de imágenes Docker.
- run.sh (create) - Script para validar Docker, construir, iniciar los servicios, esperar a que estén saludables e imprimir la URL de acceso.
- README.md (create) - Documentación del proyecto, incluyendo prerrequisitos, cómo clonar, ejecutar y probar.
**Dependencies:** All previous items
**Validation:** './run.sh' se ejecuta sin errores, todos los servicios reportan estar saludables, la aplicación web es accesible en `localhost:21000` y todas las funcionalidades de la interfaz de usuario y la API responden correctamente.
**Role:** role-devops (devops_support)