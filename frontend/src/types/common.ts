/**
 * Tipos comunes de utilidad del frontend "Pre-screening para Ensayos Clínicos
 * Estado 1".
 *
 * Este módulo agrupa los tipos genéricos que comparten los hooks, los
 * clientes de API y los componentes de interfaz: forma de los errores
 * normalizados por la API, estado de carga de las operaciones asíncronas y
 * utilidades de tipado（Criterio) reutilizadas por los formularios clínicos.
 *
 * No contiene contratos de datos de negocio: esos viven en
 * `frontend/src/types/api.ts`, que es el espejo de los esquemas Pydantic del
 * backend.
 */

/** Valor admisible en los campos clínicos del formulario de evaluación. */
export type ValorCampo = string | number | boolean;

/** Opción seleccionable en los campos clínicos de tipo lista desplegable. */
export interface OpcionCampo {
  value: string | number;
  label: string;
}

/** Estado de carga y error común a las operaciones asíncronas de la API. */
export interface EstadoOperacion {
  isLoading: boolean;
  error: string | null;
}

/** Detalle de un error de validación de esquema devuelto por la API. */
export interface DetalleValidacion {
  loc: string[];
  msg: string;
  type: string;
}

/** Cuerpo de error normalizado por la API (`detail`, `code` y `details`). */
export interface RespuestaErrorApi {
  detail: string;
  code?: string;
  details?: {
    errors?: DetalleValidacion[];
    [clave: string]: unknown;
  };
}

/** Resultado de una operación que puede fallar sin propagar excepciones. */
export type ResultadoOperacion<T> =
  | { ok: true; valor: T }
  | { ok: false; error: string };

/** Elimina `null` y `undefined` del tipo. */
export type NoNulo<T> = T extends null | undefined ? never : T;

/** Marca como opcionales todas las propiedades de un tipo. */
export type Parcial<T> = { [K in keyof T]?: T[K] };

/** Extracción de las claves de un tipo de objeto. */
export type Clave<T> = keyof T;

/** Extracción de los valores admitidos por un tipo de objeto. */
export type Valor<T> = T[keyof T];

/** Función de ordenación estable para listados clínicos. */
export type Orden<T> = (a: T, b: T) => number;

/** Lista sin elementos nulos ni indefinidos. */
export type ListaDefinida<T> = Array<Exclude<T, null | undefined>>;
