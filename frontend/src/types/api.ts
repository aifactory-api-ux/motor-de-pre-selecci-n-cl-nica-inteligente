/**
 * Contratos de datos de la API del proyecto "Pre-screening para Ensayos
 * Clínicos Estado 1".
 *
 * Este módulo reproduce exactamente los esquemas Pydantic definidos en
 * `backend/shared/schemas.py`: mismos nombres de campo, misma obligatoriedad y
 * mismos tipos. Cualquier evolución del backend debe reflejarse aquí para que
 * el frontend y la API compartan una única definición de la interfaz.
 *
 * Convenciones de serialización:
 *   - Los identificadores `UUID` viajan como cadenas de texto.
 *   - Las fechas viajan como cadenas ISO (`YYYY-MM-DD`), tal y como las
 *     serializa FastAPI a partir de los tipos `date` de Python.
 *   - Los campos de PII (`codigo_interno`, `seudonimo`, `datos_clinicos`)
 *     llegan enmascarados por el backend conforme a GDPR/HIPAA.
 */

import type { ReactNode } from 'react';

/** Identificador único de un recurso de la API. */
export type UUID = string;

/** Fecha en formato ISO (`YYYY-MM-DD`) serializada por FastAPI. */
export type FechaISO = string;

/** Roles de usuario admitidos por la API. */
export type RolUsuario = 'investigador' | 'gestor';

/** Naturaleza admitida para un criterio de protocolo. */
export type TipoCriterio = 'inclusion' | 'exclusion';

/** Veredictos admitidos para una evaluación. */
export type ResultadoEvaluacion = 'elegible' | 'noElegible' | 'pendiente';

/** Estados admitidos en el ciclo de vida de una evaluación. */
export type EstadoEvaluacion = 'pendiente' | 'completada' | 'en_revision';

// --- USUARIO ---
export interface UsuarioBase {
  nombre: string;
  email: string;
  rol: RolUsuario;
  activo: boolean;
}

export interface UsuarioCreate extends UsuarioBase {
  password: string;
}

export interface UsuarioResponse extends UsuarioBase {
  id: UUID;
}

// --- PACIENTE ---
export interface PacienteBase {
  codigo_interno: string;
  seudonimo: string;
  fecha_nacimiento: FechaISO;
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
  fecha_vigencia: FechaISO;
  descripcion: string;
}

export interface ProtocoloResponse extends ProtocoloBase {
  id: UUID;
}

// --- CRITERIO ---
export interface CriterioBase {
  protocolo_id: UUID;
  tipo: TipoCriterio;
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
  fecha_inicio: FechaISO;
  fecha_fin?: FechaISO;
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
  fecha_diagnostico: FechaISO;
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
  fecha_evaluacion: FechaISO;
  resultado?: ResultadoEvaluacion;
  estado: EstadoEvaluacion;
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
  fecha_registro: FechaISO;
  regla_rechazo?: string;
  detalle: string;
  hash_encadenado: string;
}

export interface AuditLogResponse extends AuditLogBase {
  id: UUID;
}

// --- AUTENTICACIÓN ---
export interface LoginRequest {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface TokenData {
  email?: string;
}

// --- MÉTRICAS ---
export interface MotivoRechazo {
  motivo: string;
  count: number;
}

export interface EvaluationMetrics {
  total_evaluaciones: number;
  elegibles: number;
  no_elegibles: number;
  pendientes: number;
  motivos_rechazo_top: MotivoRechazo[];
}

// --- DataTable ---
export interface DataColumn {
  key: string;
  header: string;
  render?: (row: RowData) => ReactNode;
}

export interface RowData {
  id: UUID;
  [key: string]: any;
}
