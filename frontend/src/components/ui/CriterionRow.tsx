/**
 * Fila de evaluación de un criterio de inclusión o de exclusión.
 *
 * Muestra de forma legible qué criterio se aplicó, el valor observado en el
 * paciente y por qué el criterio aportó elegibilidad o rechazo. El estado se
 * apoya en ícono y texto además del color.
 *
 * Todos los valores visuales provienen de `frontend/src/styles/tokens.ts`.
 */

import type { ReactNode } from 'react';
import { AlertTriangle, CheckCircle2, MinusCircle, XCircle } from 'lucide-react';

import { tokens } from '../../styles/tokens';

/** Estados evaluables de un criterio del protocolo. */
export type EstadoCriterio = 'cumplido' | 'bloqueante' | 'noEvaluado' | 'advertencia';

export interface CriterionRowProps {
  criterion: string;
  value?: string;
  status: EstadoCriterio;
  detail?: string;
}

/** Descripción textual de cada estado evaluable. */
const ETIQUETA_ESTADO: Record<EstadoCriterio, string> = {
  cumplido: 'Cumple',
  bloqueante: 'Bloqueante',
  noEvaluado: 'No evaluado',
  advertencia: 'Advertencia',
};

/** Paleta e ícono de cada estado evaluable. */
const ESTILOS_ESTADO: Record<
  EstadoCriterio,
  { fondo: string; texto: string; icono: ReactNode }
> = {
  cumplido: {
    fondo: tokens.colors.successSubtle,
    texto: tokens.colors.success,
    icono: (
      <CheckCircle2
        size={tokens.iconography.sizes.sm}
        strokeWidth={1.75}
        aria-hidden="true"
      />
    ),
  },
  bloqueante: {
    fondo: tokens.colors.dangerSubtle,
    texto: tokens.colors.danger,
    icono: (
      <XCircle size={tokens.iconography.sizes.sm} strokeWidth={1.75} aria-hidden="true" />
    ),
  },
  noEvaluado: {
    fondo: tokens.colors.surfaceAlt,
    texto: tokens.colors.textSecondary,
    icono: (
      <MinusCircle
        size={tokens.iconography.sizes.sm}
        strokeWidth={1.75}
        aria-hidden="true"
      />
    ),
  },
  advertencia: {
    fondo: tokens.colors.warningSubtle,
    texto: tokens.colors.warning,
    icono: (
      <AlertTriangle
        size={tokens.iconography.sizes.sm}
        strokeWidth={1.75}
        aria-hidden="true"
      />
    ),
  },
};

/**
 * Fila con el criterio evaluado, su valor y el estado resultante.
 */
export function CriterionRow({
  criterion,
  value,
  status,
  detail,
}: CriterionRowProps) {
  const estilos = ESTILOS_ESTADO[status];
  const rotulo = tokens.typography.scale.label;
  const cuerpo = tokens.typography.scale.bodySmall;
  const insignia = tokens.typography.scale.caption;

  return (
    <div
      className="flex flex-col gap-2 border-b py-3 last:border-b-0"
      style={{ borderColor: tokens.colors.border }}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex min-w-0 items-start gap-2.5">
          <span
            className="mt-0.5 shrink-0"
            style={{ color: estilos.texto }}
          >
            {estilos.icono}
          </span>

          <div className="min-w-0">
            <p
              style={{
                fontSize: rotulo.size,
                lineHeight: rotulo.lineHeight,
                fontWeight: rotulo.weight,
                color: tokens.colors.textPrimary,
              }}
            >
              {criterion}
            </p>

            {detail ? (
              <p
                className="mt-1"
                style={{
                  fontSize: cuerpo.size,
                  lineHeight: cuerpo.lineHeight,
                  color: tokens.colors.textSecondary,
                }}
              >
                {detail}
              </p>
            ) : null}
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2">
          {value ? (
            <span
              className="px-2.5 py-1"
              style={{
                backgroundColor: tokens.colors.surfaceAlt,
                borderRadius: tokens.borderRadius.sm,
                color: tokens.colors.textSecondary,
                fontSize: insignia.size,
                lineHeight: insignia.lineHeight,
                fontWeight: 600,
                whiteSpace: 'nowrap',
              }}
            >
              {value}
            </span>
          ) : null}

          <span
            className="inline-flex items-center gap-1.5 px-2.5 py-1"
            style={{
              backgroundColor: estilos.fondo,
              borderRadius: tokens.borderRadius.pill,
              color: estilos.texto,
              fontSize: insignia.size,
              lineHeight: insignia.lineHeight,
              fontWeight: 600,
              whiteSpace: 'nowrap',
            }}
          >
            {estilos.icono}
            {ETIQUETA_ESTADO[status]}
          </span>
        </div>
      </div>
    </div>
  );
}

export default CriterionRow;
