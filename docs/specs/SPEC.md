```markdown
# SPEC.md

## 1. TECHNOLOGY STACK

*   **Backend:**
    *   Python 3.10+
    *   FastAPI 0.104.1
    *   Pydantic 2.5.3
    *   SQLAlchemy 2.0.23 (for ORM)
    *   psycopg2-binary (PostgreSQL adapter)
    *   python-jose (for JWT authentication)
    *   passlib (for password hashing)
    *   uvicorn (ASGI server)
*   **Frontend:**
    *   React 18.2.0
    *   TypeScript 5.2.2
    *   Vite 5.0.0 (build tool)
    *   React Router DOM 6.21.1 (for routing)
    *   Tailwind CSS 3.4.0 (for utility-first styling, integrated with design tokens)
    *   Lucide React 0.300.0 (for iconography)
*   **Database:**
    *   PostgreSQL 16.1

## 2. DATA CONTRACTS

### Python Pydantic Models (backend/shared/schemas.py)

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from uuid import UUID, uuid4

# Base model for common fields
class BaseSchema(BaseModel):
    id: UUID = Field(default_factory=uuid4)

# --- USUARIO ---
class UsuarioBase(BaseModel):
    nombre: str
    email: str
    rol: str # 'investigador' | 'gestor'
    activo: bool = True

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioResponse(UsuarioBase):
    id: UUID

    class Config:
        from_attributes = True

# --- PACIENTE ---
class PacienteBase(BaseModel):
    codigo_interno: str = Field(description="Código interno enmascarado del paciente")
    seudonimo: str = Field(description="Seudónimo del paciente, enmascarado")
    fecha_nacimiento: date
    genero: str
    datos_clinicos: str = Field(description="Datos clínicos relevantes, enmascarados o anonimizados")

class PacienteCreate(PacienteBase):
    pass

class PacienteUpdate(PacienteBase):
    pass

class PacienteResponse(PacienteBase):
    id: UUID

    class Config:
        from_attributes = True

# --- PROTOCOLO ---
class ProtocoloBase(BaseModel):
    nombre: str
    version: str
    fecha_vigencia: date
    descripcion: str

class ProtocoloResponse(ProtocoloBase):
    id: UUID

    class Config:
        from_attributes = True

# --- CRITERIO ---
class CriterioBase(BaseModel):
    protocolo_id: UUID
    tipo: str # 'inclusion' | 'exclusion'
    codigo: str
    descripcion: str
    umbral: str # e.g., "edad >= 18", "PASI >= 10"

class CriterioResponse(CriterioBase):
    id: UUID

    class Config:
        from_attributes = True

# --- MEDICACION ---
class MedicacionBase(BaseModel):
    paciente_id: UUID
    nombre: str
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    tipo: str

class MedicacionCreate(MedicacionBase):
    pass

class MedicacionResponse(MedicacionBase):
    id: UUID

    class Config:
        from_attributes = True

# --- CONDICION_MEDICA ---
class CondicionMedicaBase(BaseModel):
    paciente_id: UUID
    diagnostico: str
    fecha_diagnostico: date
    detalle: str

class CondicionMedicaCreate(CondicionMedicaBase):
    pass

class CondicionMedicaResponse(CondicionMedicaBase):
    id: UUID

    class Config:
        from_attributes = True

# --- EVALUACION ---
class EvaluacionBase(BaseModel):
    paciente_id: UUID
    usuario_id: UUID
    protocolo_id: UUID
    fecha_evaluacion: date
    resultado: Optional[str] = None # 'elegible' | 'noElegible' | 'pendiente'
    estado: str = Field(default="pendiente") # 'pendiente' | 'completada' | 'en_revision'

class EvaluacionCreate(BaseModel):
    paciente_id: UUID
    protocolo_id: UUID

class EvaluacionSubmitData(BaseModel):
    # Fields representing patient's current clinical data for evaluation
    edad: int
    pasi_score: float
    bsa_score: float
    psoriasis_cronica_meses: int
    historial_tb: bool
    embarazo: bool
    biologicos_corticoides_recientes: bool
    # Add other relevant clinical data points as needed for the protocol ALM-PSO-2026

class EvaluacionResponse(EvaluacionBase):
    id: UUID
    paciente: PacienteResponse
    protocolo: ProtocoloResponse
    usuario: UsuarioResponse # Simplified for response, might be just ID in some contexts

    class Config:
        from_attributes = True

# --- REGLA_EVALUACION ---
class ReglaEvaluacionBase(BaseModel):
    evaluacion_id: UUID
    criterio_id: UUID
    cumple: bool
    motivo_rechazo: Optional[str] = None
    valor_paciente: Optional[str] = None
    umbral_evaluado: Optional[str] = None

class ReglaEvaluacionResponse(ReglaEvaluacionBase):
    id: UUID
    criterio: CriterioResponse # Include criterion details

    class Config:
        from_attributes = True

# --- AUDIT_LOG ---
class AuditLogBase(BaseModel):
    evaluacion_id: UUID
    usuario_id: UUID
    fecha_registro: date
    regla_rechazo: Optional[str] = None
    detalle: str
    hash_encadenado: str = Field(description="Hash encadenado para inmutabilidad GxP")

class AuditLogResponse(AuditLogBase):
    id: UUID

    class Config:
        from_attributes = True

# --- AUTHENTICATION ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- METRICS ---
class EvaluationMetrics(BaseModel):
    total_evaluaciones: int
    elegibles: int
    no_elegibles: int
    pendientes: int
    motivos_rechazo_top: List[dict] # e.g., [{"motivo": "Edad", "count": 10}]
    # Add more metrics as needed for "Panel de reclutamiento"
```

### TypeScript Interfaces (frontend/src/types/api.ts)

```typescript
import { ReactNode } from 'react';

export type UUID = string; // UUIDs are represented as strings in TypeScript

// --- USUARIO ---
export interface UsuarioBase {
    nombre: string;
    email: string;
    rol: 'investigador' | 'gestor';
    activo: boolean;
}

export interface UsuarioCreate extends UsuarioBase {
    password?: string; // Password is only for creation/update, not typically returned
}

export interface UsuarioResponse extends UsuarioBase {
    id: UUID;
}

// --- PACIENTE ---
export interface PacienteBase {
    codigo_interno: string;
    seudonimo: string;
    fecha_nacimiento: string; // ISO date string
    genero: string;
    datos_clinicos: string;
}

export interface PacienteCreate extends PacienteBase {}
export interface PacienteUpdate extends PacienteBase {}

export interface PacienteResponse extends PacienteBase {
    id: UUID;
}

// --- PROTOCOLO ---
export interface ProtocoloBase {
    nombre: string;
    version: string;
    fecha_vigencia: string; // ISO date string
    descripcion: string;
}

export interface ProtocoloResponse extends ProtocoloBase {
    id: UUID;
}

// --- CRITERIO ---
export interface CriterioBase {
    protocolo_id: UUID;
    tipo: 'inclusion' | 'exclusion';
    codigo: string;
    descripcion: string;
    umbral: string;
}

export interface CriterioResponse extends CriterioBase {
    id: UUID;
}

// --- MEDICACION ---
export interface MedicacionBase {
    paciente_id: UUID;
    nombre: string;
    fecha_inicio: string; // ISO date string
    fecha_fin?: string; // ISO date string
    tipo: string;
}

export interface MedicacionCreate extends MedicacionBase {}
export interface MedicacionResponse extends MedicacionBase {
    id: UUID;
}

// --- CONDICION_MEDICA ---
export interface CondicionMedicaBase {
    paciente_id: UUID;
    diagnostico: string;
    fecha_diagnostico: string; // ISO date string
    detalle: string;
}

export interface CondicionMedicaCreate extends CondicionMedicaBase {}
export interface CondicionMedicaResponse extends CondicionMedicaBase {
    id: UUID;
}

// --- EVALUACION ---
export interface EvaluacionBase {
    paciente_id: UUID;
    usuario_id: UUID;
    protocolo_id: UUID;
    fecha_evaluacion: string; // ISO date string
    resultado?: 'elegible' | 'noElegible' | 'pendiente';
    estado: 'pendiente' | 'completada' | 'en_revision';
}

export interface EvaluacionCreate {
    paciente_id: UUID;
    protocolo_id: UUID;
}

export interface EvaluacionSubmitData {
    edad: number;
    pasi_score: number;
    bsa_score: number;
    psoriasis_cronica_meses: number;
    historial_tb: boolean;
    embarazo: boolean;
    biologicos_corticoides_recientes: boolean;
}

export interface EvaluacionResponse extends EvaluacionBase {
    id: UUID;
    paciente: PacienteResponse;
    protocolo: ProtocoloResponse;
    usuario: UsuarioResponse;
}

// --- REGLA_EVALUACION ---
export interface ReglaEvaluacionBase {
    evaluacion_id: UUID;
    criterio_id: UUID;
    cumple: boolean;
    motivo_rechazo?: string;
    valor_paciente?: string;
    umbral_evaluado?: string;
}

export interface ReglaEvaluacionResponse extends ReglaEvaluacionBase {
    id: UUID;
    criterio: CriterioResponse;
}

// --- AUDIT_LOG ---
export interface AuditLogBase {
    evaluacion_id: UUID;
    usuario_id: UUID;
    fecha_registro: string; // ISO date string
    regla_rechazo?: string;
    detalle: string;
    hash_encadenado: string;
}

export interface AuditLogResponse extends AuditLogBase {
    id: UUID;
}

// --- AUTHENTICATION ---
export interface Token {
    access_token: string;
    token_type: string;
}

// --- METRICS ---
export interface EvaluationMetrics {
    total_evaluaciones: number;
    elegibles: number;
    no_elegibles: number;
    pendientes: number;
    motivos_rechazo_top: { motivo: string; count: number }[];
}

// --- DataTable specific types ---
export interface DataColumn {
    key: string;
    header: string;
    render?: (row: RowData) => ReactNode;
}

export interface RowData {
    id: UUID;
    [key: string]: any;
}
```

## 3. API ENDPOINTS

### Authentication Endpoints

*   **POST /auth/login**
    *   **Description:** Authenticates a user and returns an access token.
    *   **Request Body:** `UsuarioCreate` (only `email` and `password` are used)
    *   **Response:** `Token`
*   **GET /users/me**
    *   **Description:** Retrieves the currently authenticated user's information.
    *   **Authentication:** Required (JWT)
    *   **Response:** `UsuarioResponse`

### Patient Endpoints

*   **POST /pacientes**
    *   **Description:** Creates a new patient record with masked PII.
    *   **Authentication:** Required (investigador/gestor role)
    *   **Request Body:** `PacienteCreate`
    *   **Response:** `PacienteResponse`
*   **GET /pacientes/{paciente_id}**
    *   **Description:** Retrieves details for a specific patient.
    *   **Authentication:** Required (investigador/gestor role)
    *   **Response:** `PacienteResponse`
*   **PUT /pacientes/{paciente_id}**
    *   **Description:** Updates details for a specific patient.
    *   **Authentication:** Required (investigador/gestor role)
    *   **Request Body:** `PacienteUpdate`
    *   **Response:** `PacienteResponse`

### Protocol Endpoints

*   **GET /protocolos**
    *   **Description:** Lists all available clinical protocols.
    *   **Authentication:** Required
    *   **Response:** `List[ProtocoloResponse]`
*   **GET /protocolos/{protocolo_id}**
    *   **Description:** Retrieves details for a specific protocol.
    *   **Authentication:** Required
    *   **Response:** `ProtocoloResponse`

### Criterion Endpoints

*   **GET /protocolos/{protocolo_id}/criterios**
    *   **Description:** Lists all criteria associated with a specific protocol.
    *   **Authentication:** Required
    *   **Response:** `List[CriterioResponse]`

### Evaluation Endpoints

*   **POST /evaluaciones**
    *   **Description:** Initiates a new evaluation for a patient under a specific protocol.
    *   **Authentication:** Required (investigador role)
    *   **Request Body:** `EvaluacionCreate`
    *   **Response:** `EvaluacionResponse` (initial state)
*   **GET /evaluaciones**
    *   **Description:** Lists recent evaluations, optionally filtered.
    *   **Authentication:** Required
    *   **Query Parameters:** `estado: Optional[str]`, `paciente_id: Optional[UUID]`, `usuario_id: Optional[UUID]`
    *   **Response:** `List[EvaluacionResponse]`
*   **GET /evaluaciones/{evaluacion_id}**
    *   **Description:** Retrieves full details for a specific evaluation.
    *   **Authentication:** Required
    *   **Response:** `EvaluacionResponse`
*   **POST /evaluaciones/{evaluacion_id}/submit**
    *   **Description:** Submits clinical data for an ongoing evaluation, triggers the rule engine, and updates the evaluation result and state.
    *   **Authentication:** Required (investigador role)
    *   **Request Body:** `EvaluacionSubmitData`
    *   **Response:** `EvaluacionResponse` (with updated `resultado` and `estado`)

### Rule Evaluation Endpoints

*   **GET /evaluaciones/{evaluacion_id}/reglas**
    *   **Description:** Retrieves the detailed rule evaluations for a specific completed evaluation.
    *   **Authentication:** Required
    *   **Response:** `List[ReglaEvaluacionResponse]`

### Audit Log Endpoints

*   **GET /audit-logs**
    *   **Description:** Retrieves a list of all audit logs, with optional filters.
    *   **Authentication:** Required (gestor role)
    *   **Query Parameters:** `evaluacion_id: Optional[UUID]`, `usuario_id: Optional[UUID]`, `fecha_inicio: Optional[date]`, `fecha_fin: Optional[date]`
    *   **Response:** `List[AuditLogResponse]`

### Metrics Endpoints

*   **GET /metrics/evaluaciones**
    *   **Description:** Provides aggregated statistics on evaluations (e.g., total, eligible, non-eligible, top rejection reasons).
    *   **Authentication:** Required (gestor role)
    *   **Response:** `EvaluationMetrics`

## 4. FILE STRUCTURE

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI application entry point
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py             # Authentication endpoints
│   │   │   │   ├── users.py            # User-related endpoints
│   │   │   │   ├── pacientes.py        # Patient management endpoints
│   │   │   │   ├── protocolos.py       # Protocol management endpoints
│   │   │   │   ├── criterios.py        # Criterion management endpoints
│   │   │   │   ├── evaluaciones.py     # Evaluation flow endpoints
│   │   │   │   ├── reglas_evaluacion.py # Rule evaluation details endpoints
│   │   │   │   ├── audit_logs.py       # Audit log endpoints
│   │   │   │   └── metrics.py          # Metrics endpoints
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py               # Application configuration settings
│   │   │   ├── security.py             # JWT token handling, password hashing
│   │   │   └── exceptions.py           # Custom exception handlers
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py         # Business logic for authentication
│   │   │   ├── patient_service.py      # Business logic for patient operations
│   │   │   ├── protocol_service.py     # Business logic for protocol operations
│   │   │   ├── evaluation_service.py   # Business logic for evaluation flow and rule engine
│   │   │   ├── audit_service.py        # Business logic for audit logging
│   │   │   └── metrics_service.py      # Business logic for metrics calculation
│   │   └── rules_engine/
│   │       ├── __init__.py
│   │       └── protocol_alm_pso_2026.py # Rule definitions and evaluation logic for ALM-PSO-2026
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py                   # SQLAlchemy ORM models (mirroring ERD)
│   │   ├── session.py                  # Database session management
│   │   └── crud.py                     # CRUD operations for database models
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── schemas.py                  # Pydantic models for API (Data Contracts)
│   │   ├── dependencies.py             # Common FastAPI dependencies (e.g., get_db, get_current_user)
│   │   └── utils.py                    # Utility functions (e.g., PII masking, hash chaining)
│   ├── requirements.txt                # Python dependencies
│   └── Dockerfile                      # Dockerfile for backend service
├── frontend/
│   ├── public/
│   │   └── index.html                  # Main HTML file
│   ├── src/
│   │   ├── main.tsx                    # Frontend entry point
│   │   ├── App.tsx                     # Main application component, handles routing
│   │   ├── index.css                   # Global styles (Tailwind base, components, utilities)
│   │   ├── api/
│   │   │   ├── auth.ts                 # API client for authentication
│   │   │   ├── patients.ts             # API client for patient endpoints
│   │   │   ├── protocols.ts            # API client for protocol endpoints
│   │   │   ├── evaluations.ts          # API client for evaluation endpoints
│   │   │   ├── auditLogs.ts            # API client for audit log endpoints
│   │   │   └── metrics.ts              # API client for metrics endpoints
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   │   ├── AppShell.tsx        # Base responsive structure with navigation
│   │   │   │   ├── PrimaryButton.tsx   # Primary CTA button
│   │   │   │   ├── ClinicalCard.tsx    # Container for clinical sections, metrics
│   │   │   │   ├── StatusPill.tsx      # Semantic label for eligibility/status
│   │   │   │   ├── CriterionRow.tsx    # Displays a single criterion and its status
│   │   │   │   ├── ClinicalField.tsx   # Input field for clinical data
│   │   │   │   ├── DataTable.tsx       # Generic table component
│   │   │   │   └── StatCard.tsx        # Card for displaying statistics
│   │   │   └── common/
│   │   │       ├── LoadingSpinner.tsx  # Generic loading spinner
│   │   │       └── ErrorMessage.tsx    # Generic error message display
│   │   ├── hooks/
│   │   │   ├── useAuth.ts              # Authentication state management hook
│   │   │   ├── usePatients.ts          # Patient data fetching and mutation hook
│   │   │   ├── useEvaluations.ts       # Evaluation data fetching and mutation hook
│   │   │   ├── useAuditLogs.ts         # Audit log data fetching hook
│   │   │   └── useMetrics.ts           # Metrics data fetching hook
│   │   ├── pages/
│   │   │   ├── AccesoSeguro.tsx        # Login page
│   │   │   ├── CentroDeEvaluaciones.tsx # Dashboard for evaluations
│   │   │   ├── FormularioDeEvaluacionClinica.tsx # Patient evaluation form
│   │   │   ├── ResolucionDeElegibilidad.tsx # Evaluation result display
│   │   │   ├── AuditoriaYTrazabilidad.tsx # Audit log review page
│   │   │   └── PanelDeReclutamiento.tsx # Recruitment statistics dashboard
│   │   ├── styles/
│   │   │   ├── tokens.ts               # Design tokens (colors, typography, spacing, etc.)
│   │   │   └── tailwind.css            # Tailwind CSS directives
│   │   └── types/
│   │       ├── api.ts                  # TypeScript interfaces for API data contracts
│   │       └── common.ts               # Common utility types
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── Dockerfile                      # Dockerfile for frontend service
├── docker-compose.yml                  # Docker Compose configuration
├── .env.example                        # Example environment variables
├── .gitignore                          # Git ignore file
└── README.md                           # Project README
```

**PORT TABLE**

| Service           | Listening Port | Path                  |
| :---------------- | :------------- | :-------------------- |
| frontend-service  | 21000          | frontend/             |
| backend-service   | 21001          | backend/app/          |
| db-service        | 25432          | (internal PostgreSQL) |

**SHARED MODULES**

| Shared path     | Imported by services |
| :-------------- | :------------------- |
| backend/shared/ | backend-service      |

## 5. ENVIRONMENT VARIABLES

| Name                  | Type    | Description                                                              | Example Value                               |
| :-------------------- | :------ | :----------------------------------------------------------------------- | :------------------------------------------ |
| `DATABASE_URL`        | string  | PostgreSQL connection string for the backend.                            | `postgresql://user:password@db:5432/dbname` |
| `SECRET_KEY`          | string  | Secret key for JWT token encoding/decoding. Must be a strong, random string. | `supersecretkeythatshouldbechanged`         |
| `ALGORITHM`           | string  | Algorithm used for JWT signing.                                          | `HS256`                                     |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | Expiration time for access tokens in minutes.                            | `30`                                        |
| `POSTGRES_USER`       | string  | PostgreSQL database user.                                                | `user`                                      |
| `POSTGRES_PASSWORD`   | string  | PostgreSQL database password.                                            | `password`                                  |
| `POSTGRES_DB`         | string  | PostgreSQL database name.                                                | `clinical_screening_db`                     |
| `BACKEND_URL`         | string  | URL where the backend API is accessible.                                 | `http://localhost:21001`                    |
| `FRONTEND_URL`        | string  | URL where the frontend is accessible (for CORS).                         | `http://localhost:21000`                    |

## 6. IMPORT CONTRACTS

### Backend (Python)

*   `from backend.shared.schemas import UsuarioCreate, UsuarioResponse, PacienteCreate, PacienteResponse, ProtocoloResponse, CriterioResponse, EvaluacionCreate, EvaluacionSubmitData, EvaluacionResponse, ReglaEvaluacionResponse, AuditLogResponse, Token, EvaluationMetrics`
*   `from backend.database.models import Usuario, Paciente, Protocolo, Criterio, Medicacion, CondicionMedica, Evaluacion, ReglaEvaluacion, AuditLog`
*   `from backend.database.session import get_db`
*   `from backend.app.core.config import settings`
*   `from backend.app.core.security import create_access_token, verify_password, get_password_hash, get_current_user`
*   `from backend.shared.dependencies import get_current_active_user, get_current_active_investigador, get_current_active_gestor`
*   `from backend.app.services.auth_service import AuthService`
*   `from backend.app.services.patient_service import PatientService`
*   `from backend.app.services.evaluation_service import EvaluationService`
*   `from backend.app.rules_engine.protocol_alm_pso_2026 import evaluate_protocol_alm_pso_2026`
*   `from backend.shared.utils import mask_pii_data, generate_chained_hash`

### Frontend (TypeScript)

*   `import { UsuarioResponse, PacienteCreate, PacienteResponse, ProtocoloResponse, CriterioResponse, EvaluacionCreate, EvaluacionSubmitData, EvaluacionResponse, ReglaEvaluacionResponse, AuditLogResponse, Token, EvaluationMetrics, DataColumn, RowData, UUID } from '../types/api';`
*   `import { login, getMe, createPatient, getPatient, updatePatient, getProtocols, getCriteriaForProtocol, createEvaluation, getEvaluations, getEvaluationDetails, submitEvaluation, getRuleEvaluations, getAuditLogs, getEvaluationMetrics } from '../api/index';` (or specific API client files)
*   `import { useAuth } from '../hooks/useAuth';`
*   `import { usePatients } from '../hooks/usePatients';`
*   `import { useEvaluations } from '../hooks/useEvaluations';`
*   `import { useAuditLogs } from '../hooks/useAuditLogs';`
*   `import { useMetrics } from '../hooks/useMetrics';`
*   `import { tokens } from '../styles/tokens';`
*   `import { AppShell } from '../components/ui/AppShell';`
*   `import { PrimaryButton } from '../components/ui/PrimaryButton';`
*   `import { ClinicalCard } from '../components/ui/ClinicalCard';`
*   `import { StatusPill } from '../components/ui/StatusPill';`
*   `import { CriterionRow } from '../components/ui/CriterionRow';`
*   `import { ClinicalField } from '../components/ui/ClinicalField';`
*   `import { DataTable } from '../components/ui/DataTable';`
*   `import { StatCard } from '../components/ui/StatCard';`

## 7. FRONTEND STATE & COMPONENT CONTRACTS

### Shared State Primitives (React Hooks)

*   `useAuth()`
    *   Returns: `{ user: UsuarioResponse | null, login: (credentials: UsuarioCreate) => Promise<void>, logout: () => void, isLoading: boolean, error: string | null }`
*   `usePatients()`
    *   Returns: `{ patients: PacienteResponse[], isLoading: boolean, error: string | null, fetchPatients: () => Promise<void>, createPatient: (data: PacienteCreate) => Promise<PacienteResponse | null>, updatePatient: (id: UUID, data: PacienteUpdate) => Promise<PacienteResponse | null> }`
*   `useEvaluations()`
    *   Returns: `{ evaluations: EvaluacionResponse[], isLoading: boolean, error: string | null, fetchEvaluations: (filters?: { estado?: string, paciente_id?: UUID, usuario_id?: UUID }) => Promise<void>, createEvaluation: (data: EvaluacionCreate) => Promise<EvaluacionResponse | null>, submitEvaluation: (id: UUID, data: EvaluacionSubmitData) => Promise<EvaluacionResponse | null> }`
*   `useEvaluationDetails(id: UUID)`
    *   Returns: `{ evaluation: EvaluacionResponse | null, isLoading: boolean, error: string | null, fetchEvaluationDetails: () => Promise<void>, ruleEvaluations: ReglaEvaluacionResponse[], fetchRuleEvaluations: () => Promise<void> }`
*   `useAuditLogs()`
    *   Returns: `{ auditLogs: AuditLogResponse[], isLoading: boolean, error: string | null, fetchAuditLogs: (filters?: { evaluacion_id?: UUID, usuario_id?: UUID, fecha_inicio?: string, fecha_fin?: string }) => Promise<void> }`
*   `useMetrics()`
    *   Returns: `{ metrics: EvaluationMetrics | null, isLoading: boolean, error: string | null, fetchMetrics: () => Promise<void> }`

### Reusable Component Props Interfaces

*   `AppShell` props/inputs: `{ children: ReactNode, role: 'investigador' | 'gestor', activeView: string, onNavigate: (view: string) => void }`
*   `PrimaryButton` props/inputs: `{ label: string, onClick: MouseEventHandler<HTMLButtonElement>, variant?: 'primary' | 'secondary' | 'danger' | 'ghost', size?: 'sm' | 'md' | 'lg', icon?: ReactNode, disabled?: boolean, loading?: boolean }`
*   `ClinicalCard` props/inputs: `{ title?: string, subtitle?: string, children: ReactNode, tone?: 'default' | 'success' | 'danger' | 'warning' | 'info', icon?: ReactNode }`
*   `StatusPill` props/inputs: `{ label: string, tone: 'elegible' | 'noElegible' | 'pendiente' | 'revision', withIcon?: boolean }`
*   `CriterionRow` props/inputs: `{ criterion: string, value?: string, status: 'cumplido' | 'bloqueante' | 'noEvaluado' | 'advertencia', detail?: string }`
*   `ClinicalField` props/inputs: `{ label: string, value: string | number | boolean, onChange: (value: string | number | boolean) => void, type?: 'text' | 'number' | 'select' | 'date' | 'boolean', unit?: string, error?: string, disabled?: boolean, masked?: boolean, options?: { value: string | number, label: string }[] }`
*   `DataTable` props/inputs: `{ columns: DataColumn[], rows: RowData[], onRowClick?: (rowId: UUID) => void, emptyState?: ReactNode, loading?: boolean }`
*   `StatCard` props/inputs: `{ label: string, value: string | number, delta?: string, tone?: 'default' | 'success' | 'danger' | 'warning' }`

## 8. FILE EXTENSION CONVENTION

*   Frontend files: `.tsx` for React components and `.ts` for utility files, hooks, and API clients.
*   The project is a TypeScript project for the frontend.
*   Exact entry point path: `frontend/src/main.tsx`

## 9. DESIGN TOKENS

```typescript
export const tokens = {
  colors: {
    background: "#F6F8FB",
    surface: "#FFFFFF",
    surfaceAlt: "#EEF3F8",
    border: "#D9E2EC",
    borderStrong: "#B9C6D4",
    textPrimary: "#0D1B2A",
    textSecondary: "#526374",
    textTertiary: "#718295",
    primary: "#0E5E9E",
    primaryHover: "#0B4E84",
    primarySubtle: "#E8F1FA",
    accent: "#007A87",
    accentSubtle: "#E6F4F5",
    success: "#1F7A4D",
    successSubtle: "#EAF5EF",
    danger: "#B3261E",
    dangerSubtle: "#FCECEB",
    warning: "#A96B00",
    warningSubtle: "#FFF5E2",
    info: "#0E5E9E",
    focusRing: "#0E5E9E",
    overlay: "rgba(13, 27, 42, 0.45)"
  },
  typography: {
    fontFamily: "Inter, system-ui, -apple-system, sans-serif",
    scale: {
      display: {
        size: "30px",
        lineHeight: "38px",
        weight: "700"
      },
      h1: {
        size: "24px",
        lineHeight: "32px",
        weight: "700"
      },
      h2: {
        size: "20px",
        lineHeight: "28px",
        weight: "600"
      },
      h3: {
        size: "16px",
        lineHeight: "24px",
        weight: "600"
      },
      body: {
        size: "16px",
        lineHeight: "24px",
        weight: "400"
      },
      bodySmall: {
        size: "14px",
        lineHeight: "20px",
        weight: "400"
      },
      label: {
        size: "14px",
        lineHeight: "20px",
        weight: "500"
      },
      caption: {
        size: "12px",
        lineHeight: "16px",
        weight: "400"
      }
    }
  },
  spacing: {
    "0": "0px",
    "1": "4px",
    "2": "8px",
    "3": "12px",
    "4": "16px",
    "5": "20px",
    "6": "24px",
    "7": "32px",
    "8": "40px",
    "9": "48px",
    "10": "64px"
  },
  borderRadius: {
    sm: "6px",
    md: "8px",
    lg: "12px",
    xl: "16px",
    pill: "999px"
  },
  shadows: {
    none: "none",
    sm: "0 1px 2px rgba(13, 27, 42, 0.05)",
    md: "0 4px 12px rgba(13, 27, 42, 0.08)",
    lg: "0 12px 32px rgba(13, 27, 42, 0.12)",
    focus: "0 0 0 3px rgba(14, 94, 158, 0.18)"
  },
  iconography: {
    style: "Lucide React, linear, stroke 1.75px",
    sizes: {
      sm: "16px",
      md: "20px",
      lg: "24px",
      xl: "32px"
    },
    usage: "Íconos lineales y descriptivos, nunca decorativos sin contexto. Los estados clínicos usan ícono más punto de color para evitar depender solo del color."
  },
  motion: {
    durationFast: "120ms",
    durationBase: "180ms",
    durationSlow: "260ms",
    easing: "cubic-bezier(0.2, 0, 0, 1)",
    prefersReducedMotion: true,
    transitions: [
      "Transiciones de tarjetas y resultados con fade + desplazamiento mínimo de 4-8px.",
      "Botones primarios cambian de estado con hover/focus/active, sin animación llamativa.",
      "El veredicto Elegible/No Elegible aparece con un refuerzo de color pero sin movimiento agresivo."
    ]
  },
  accessibility: {
    contrast: "Contraste AA mínimo en textos y AAA en estado de veredicto y errores.",
    focusVisible: "Anillo de foco visible en todos los controles interactivos.",
    targetSize: "Área mínima de interacción de 44x44px para controles táctiles en tablet.",
    forms: "Etiquetas visibles, mensajes de error asociados con aria-live y validación clara antes del envío.",
    semanticStates: "El color nunca es el único canal para comunicar elegibilidad o error; siempre se acompaña de texto o ícono."
  }
};
```

## 10. FUNCTIONAL REQUIREMENTS COVERAGE

| Requirement | Implementation | Files |
| :---------- | :------------- | :---- |
| Proyecto "Pre-screening para Ensayos Clínicos Estado 1" | Project naming and scope adherence | README.md, docker-compose.yml |
| Arquitectura bajo normativas de privacidad clínica (GDPR/HIPAA) | PII masking, user traceability, immutable audit log | backend/shared/utils.py, backend/database/models.py, backend/app/services/patient_service.py, frontend/src/components/ui/ClinicalField.tsx |
| Trazabilidad de qué usuario evalúa a cada paciente | `EVALUACION.usuario_id` y `AUDIT_LOG.usuario_id` fields | backend/database/models.py, backend/shared/schemas.py, backend/app/api/v1/evaluaciones.py, backend/app/api/v1/audit_logs.py |
| Encriptar o enmascarar cualquier campo de identificación personal (PII) | `PACIENTE.seudonimo`, `PACIENTE.codigo_interno` fields; `mask_pii_data` utility function; `masked` prop in `ClinicalField` | backend/database/models.py, backend/shared/schemas.py, backend/shared/utils.py, frontend/src/components/ui/ClinicalField.tsx, frontend/src/pages/FormularioDeEvaluacionClinica.tsx |
| Motor de pre-screening para psoriasis en placas, protocolo ALM-PSO-2026 | Dedicated rule engine logic for ALM-PSO-2026 criteria | backend/app/rules_engine/protocol_alm_pso_2026.py, backend/app/services/evaluation_service.py |
| Criterios clave: edad ≥ 18, psoriasis crónica ≥ 6 meses, PASI ≥ 10, BSA ≥ 10%; exclusiones con TB, embarazo y tratamientos recientes | `CRITERIO` model definition; rule engine logic implements these specific thresholds | backend/database/models.py, backend/shared/schemas.py, backend/app/rules_engine/protocol_alm_pso_2026.py |
| La elegibilidad siempre combina color + texto + icono | `StatusPill` component with `tone` and `withIcon` props; `ClinicalCard` with `tone` and `icon` props; `CriterionRow` with `status` prop | frontend/src/components/ui/StatusPill.tsx, frontend/src/components/ui/ClinicalCard.tsx, frontend/src/components/ui/CriterionRow.tsx, frontend/src/pages/ResolucionDeElegibilidad.tsx |
| Audit trail inmutable y visible para decisiones rechazadas | `AUDIT_LOG` and `REGLA_EVALUACION` models; `hash_encadenado` field; `AuditoriaYTrazabilidad` page | backend/database/models.py, backend/shared/schemas.py, backend/shared/utils.py, backend/app/services/audit_service.py, frontend/src/pages/AuditoriaYTrazabilidad.tsx |
| Optimizado para consulta sobre tablet/iPad: baja fricción, foco visible, validación local y carga cognitiva controlada | Responsive frontend design using design tokens and base components; client-side form validation | frontend/src/styles/tokens.ts, frontend/src/components/ui/*.tsx, frontend/src/pages/*.tsx, frontend/src/hooks/*.ts |
| Latencia cero en la lógica booleana del protocolo médico | In-memory rule engine evaluation within `EvaluationService` | backend/app/rules_engine/protocol_alm_pso_2026.py, backend/app/services/evaluation_service.py |
| Reducción del tiempo de evaluación por paciente de 40 a menos de 2 minutos | Streamlined UI/UX, efficient API calls, fast rule engine | frontend/src/pages/FormularioDeEvaluacionClinica.tsx, frontend/src/api/*.ts, backend/app/services/evaluation_service.py |
| 100% de cumplimiento del audit trail para pacientes rechazados | Every rule evaluation and rejection reason is logged in `REGLA_EVALUACION` and `AUDIT_LOG` | backend/database/models.py, backend/shared/schemas.py, backend/app/services/evaluation_service.py, backend/app/services/audit_service.py |
| Registro inmutable de auditoría GxP | `AUDIT_LOG.hash_encadenado` field, generated using a cryptographic hash of previous log entry | backend/database/models.py, backend/shared/schemas.py, backend/shared/utils.py (for `generate_chained_hash`), backend/app/services/audit_service.py |
| Interfaz responsive en React para tablets/iPads | React frontend with Tailwind CSS and responsive design principles, using `AppShell` | frontend/src/App.tsx, frontend/src/components/ui/AppShell.tsx, frontend/src/styles/tailwind.css |
| Precisión del árbol de decisiones (evitar falsos aptos) | Rule engine logic explicitly implements inclusion/exclusion criteria | backend/app/rules_engine/protocol_alm_pso_2026.py |
| Sistema completamente independiente sin integraciones HCE | No external API calls or integration points in the backend or frontend | backend/app/main.py, frontend/src/api/*.ts (only internal API calls) |
| Ingreso manual de parámetros clínicos y tiempos de lavado por investigadores a través de la interfaz web React | `FormularioDeEvaluacionClinica` page with `ClinicalField` components | frontend/src/pages/FormularioDeEvaluacionClinica.tsx, frontend/src/components/ui/ClinicalField.tsx |
| Validación de datos clínicos contra la base de datos PostgreSQL local antes de ejecutar la evaluación | Backend services perform validation against existing patient data and protocol criteria | backend/app/services/patient_service.py, backend/app/services/evaluation_service.py |
| Endpoints en FastAPI diseñados con recursos básicos FHIR para prever escalabilidad futura | Pydantic schemas are designed with fields that align with basic FHIR resource concepts (e.g., Patient, Encounter, Observation) | backend/shared/schemas.py, backend/app/api/v1/*.py |
| Contenerización con Docker y Docker Compose para empaquetar React, FastAPI y PostgreSQL | Dockerfiles for backend and frontend, `docker-compose.yml` for orchestration | backend/Dockerfile, frontend/Dockerfile, docker-compose.yml |
| Ambientes requeridos: desarrollo local con Docker Compose, staging para validación pre-demo y producción/demo aislada para Almirall | Docker Compose setup supports consistent environments | docker-compose.yml, .env.example |
| Implementar el motor de reglas booleano con configuración declarativa para criterios de inclusión y exclusión del protocolo ALM-PSO-2026 | `protocol_alm_pso_2026.py` contains explicit, configurable rule definitions | backend/app/rules_engine/protocol_alm_pso_2026.py |
| Diseñar el esquema PostgreSQL para pacientes, evaluaciones, resultados y logs de auditoría inmutables | SQLAlchemy ORM models directly reflect the provided ERD | backend/database/models.py |
| Desarrollar los endpoints FastAPI de evaluación y auditoría con modelos Pydantic alineados a FHIR básico | API endpoints and their request/response schemas are defined in `API ENDPOINTS` and `DATA CONTRACTS` sections | backend/app/api/v1/*.py, backend/shared/schemas.py |
| Construir formularios React responsive con validación para ingreso manual en tablets/iPads | Frontend pages like `FormularioDeEvaluacionClinica` use `ClinicalField` and client-side validation | frontend/src/pages/FormularioDeEvaluacionClinica.tsx, frontend/src/components/ui/ClinicalField.tsx, frontend/src/hooks/useEvaluations.ts |
| Autenticación y autorización por roles (investigador/gestor) | JWT-based authentication; `USUARIO.rol` field; FastAPI dependencies for role-based access control | backend/database/models.py, backend/shared/schemas.py, backend/app/core/security.py, backend/shared/dependencies.py, backend/app/api/v1/auth.py |
| Mecanismo de inmutabilidad para el audit trail: hash encadenado | `AUDIT_LOG.hash_encadenado` field, calculated and stored for each new log entry based on the previous one | backend/database/models.py, backend/shared/schemas.py, backend/shared/utils.py (for `generate_chained_hash`), backend/app/services/audit_service.py |
```