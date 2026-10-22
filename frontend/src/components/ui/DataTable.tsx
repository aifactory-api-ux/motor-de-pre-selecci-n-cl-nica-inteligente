/**
 * Tabla clínica genérica para listar evaluaciones, auditorías y registros.
 *
 * Recibe la definición de columnas y las filas ya normalizadas por la capa de
 * datos, por lo que el mismo componente sirve para el listado de evaluaciones,
 * el panel de trazabilidad o cualquier registro clínico. Cada columna admite
 * un renderizado propio para insertar etiquetas de estado o datos enmascarados.
 *
 * Está pensada para su lectura en tablet: cabecera diferenciada, ancho mínimo
 * con scroll horizontal controlado y filas con estado de hover, foco visible y
 * activación por teclado cuando la tabla es navegable.
 *
 * Todos los valores visuales provienen de `frontend/src/styles/tokens.ts`.
 */

import type { KeyboardEvent, ReactNode } from 'react';
import { Inbox, Loader2 } from 'lucide-react';

import { tokens } from '../../styles/tokens';
import type { DataColumn, RowData, UUID } from '../../types/api';

export interface DataTableProps {
  columns: DataColumn[];
  rows: RowData[];
  onRowClick?: (rowId: UUID) => void;
  emptyState?: ReactNode;
  loading?: boolean;
}

/** Mensaje mostrado cuando no hay filas y el consumidor no aporta un estado vacío. */
const MENSAJE_SIN_REGISTROS = 'No hay registros para mostrar.';

/** Ancho mínimo de la tabla para conservar legibilidad en pantalla de tablet. */
const ANCHO_MINIMO = 'min-w-[640px]';

/**
 * Convierte el valor bruto de una celda en un contenido presentable.
 *
 * Los datos clínicos llegan desde la API como cadenas, números o booleanos;
 * los valores ausentes se sustituyen por un guion para no simular información.
 */
function renderValorBruto(valor: unknown): ReactNode {
  if (valor === null || valor === undefined || valor === '') {
    return '—';
  }

  if (typeof valor === 'boolean') {
    return valor ? 'Sí' : 'No';
  }

  if (typeof valor === 'object') {
    return JSON.stringify(valor);
  }

  return String(valor);
}

/**
 * Tabla de registros clínicos con soporte de carga, estado vacío y filas
 * navegables.
 */
export function DataTable({
  columns,
  rows,
  onRowClick,
  emptyState,
  loading = false,
}: DataTableProps) {
  const cabecera = tokens.typography.scale.caption;
  const cuerpo = tokens.typography.scale.bodySmall;
  const celda = tokens.typography.scale.body;
  const navegable = typeof onRowClick === 'function';
  const totalColumnas = Math.max(columns.length, 1);

  /** Activa la fila con teclado, en paridad con el clic de ratón. */
  function activarFila(evento: KeyboardEvent<HTMLTableRowElement>, rowId: UUID) {
    if (!navegable) {
      return;
    }

    if (evento.key === 'Enter' || evento.key === ' ') {
      evento.preventDefault();
      onRowClick?.(rowId);
    }
  }

  /** Obtiene el contenido de una celda, usando el renderizado propio si existe. */
  function contenidoCelda(columna: DataColumn, fila: RowData): ReactNode {
    if (columna.render) {
      return columna.render(fila);
    }

    return renderValorBruto(fila[columna.key]);
  }

  return (
    <div
      className="w-full overflow-hidden"
      style={{
        backgroundColor: tokens.colors.surface,
        border: `1px solid ${tokens.colors.border}`,
        borderRadius: tokens.borderRadius.xl,
        boxShadow: tokens.shadows.sm,
      }}
    >
      <div className="clinical-scroll w-full overflow-x-auto">
        <table className={`w-full ${ANCHO_MINIMO} border-collapse text-left`}>
          <caption className="visually-hidden">
            Listado de registros clínicos del protocolo
          </caption>

          <thead>
            <tr>
              {columns.map((columna) => (
                <th
                  key={columna.key}
                  scope="col"
                  className="px-4 py-3 whitespace-nowrap"
                  style={{
                    backgroundColor: tokens.colors.surfaceAlt,
                    color: tokens.colors.textSecondary,
                    fontSize: cabecera.size,
                    lineHeight: cabecera.lineHeight,
                    fontWeight: 600,
                    borderBottom: `1px solid ${tokens.colors.borderStrong}`,
                  }}
                >
                  {columna.header}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {loading ? (
              <tr>
                <td colSpan={totalColumnas} className="px-4 py-10">
                  <div
                    className="flex flex-col items-center justify-center gap-3"
                    role="status"
                    aria-live="polite"
                  >
                    <Loader2
                      size={tokens.iconography.sizes.lg}
                      strokeWidth={1.75}
                      className="animate-spin"
                      style={{ color: tokens.colors.primary }}
                      aria-hidden="true"
                    />
                    <span
                      style={{
                        fontSize: cuerpo.size,
                        lineHeight: cuerpo.lineHeight,
                        color: tokens.colors.textSecondary,
                      }}
                    >
                      Cargando registros…
                    </span>
                  </div>
                </td>
              </tr>
            ) : rows.length === 0 ? (
              <tr>
                <td colSpan={totalColumnas} className="px-4 py-10">
                  <div className="flex flex-col items-center justify-center gap-3 text-center">
                    <Inbox
                      size={tokens.iconography.sizes.lg}
                      strokeWidth={1.75}
                      style={{ color: tokens.colors.textTertiary }}
                      aria-hidden="true"
                    />
                    {emptyState ?? (
                      <p
                        style={{
                          fontSize: cuerpo.size,
                          lineHeight: cuerpo.lineHeight,
                          color: tokens.colors.textSecondary,
                        }}
                      >
                        {MENSAJE_SIN_REGISTROS}
                      </p>
                    )}
                  </div>
                </td>
              </tr>
            ) : (
              rows.map((fila) => (
                <tr
                  key={fila.id}
                  tabIndex={navegable ? 0 : undefined}
                  onClick={navegable ? () => onRowClick?.(fila.id) : undefined}
                  onKeyDown={
                    navegable ? (evento) => activarFila(evento, fila.id) : undefined
                  }
                  className={`transition-colors hover:bg-[var(--color-surface-alt)] ${
                    navegable
                      ? 'cursor-pointer focus:outline-none focus-visible:shadow-[var(--shadow-focus)]'
                      : ''
                  }`}
                >
                  {columns.map((columna) => (
                    <td
                      key={columna.key}
                      className="px-4 py-3 align-middle"
                      style={{
                        fontSize: celda.size,
                        lineHeight: celda.lineHeight,
                        color: tokens.colors.textPrimary,
                        borderBottom: `1px solid ${tokens.colors.border}`,
                      }}
                    >
                      {contenidoCelda(columna, fila)}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default DataTable;
