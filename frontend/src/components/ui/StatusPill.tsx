/**
 * Etiqueta semántica de elegibilidad y estado de evaluación.
 *
 * Comunica el veredicto de pre-selección combinando texto e ícono con el color
 * del matiz, de modo que el estado siga siendo legible sin depender de la
 * percepción cromática.
 *
 * Todos los valores visuales provienen de `frontend/src/styles/tokens.ts`.
 */

import type { ReactNode } from 'react';
import { AlertTriangle, CheckCircle2, Clock, XCircle } from 'lucide-react';

import { tokens } from '../../styles/tokens';

/** Estados clínicos representables con la etiqueta. */
export type TonoStatusPill = 'elegible' | 'noElegible' | 'pendiente' | 'revision';

export interface StatusPillProps {
  label: string;
  tone: TonoStatusPill;
  withIcon?: boolean;
}

/** Paleta e ícono de cada estado clínico. */
const ESTILOS_TONO: Record<
  TonoStatusPill,
  { fondo: string; texto: string; icono: ReactNode }
> = {
  elegible: {
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
  noElegible: {
    fondo: tokens.colors.dangerSubtle,
    texto: tokens.colors.danger,
    icono: (
      <XCircle size={tokens.iconography.sizes.sm} strokeWidth={1.75} aria-hidden="true" />
    ),
  },
  pendiente: {
    fondo: tokens.colors.surfaceAlt,
    texto: tokens.colors.textSecondary,
    icono: (
      <Clock size={tokens.iconography.sizes.sm} strokeWidth={1.75} aria-hidden="true" />
    ),
  },
  revision: {
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
 * Etiqueta de estado con matiz semántico e ícono opcional.
 */
export function StatusPill({ label, tone, withIcon = true }: StatusPillProps) {
  const estilos = ESTILOS_TONO[tone];
  const insignia = tokens.typography.scale.caption;

  return (
    <span
      className="inline-flex items-center gap-1.5 px-3 py-1"
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
      {withIcon ? estilos.icono : null}
      {label}
    </span>
  );
}

export default StatusPill;
