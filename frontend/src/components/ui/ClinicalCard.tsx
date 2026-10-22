/**
 * Contenedor base para secciones clínicas, métricas y resultados.
 *
 * Agrupa contenido con una jerarquía visual estable: fondo blanco, borde
 * suave y sombra ligera. El matiz semántico (`tone`) se apoya en una barra de
 * acento, un ícono y una etiqueta de texto, de modo que el estado nunca
 * dependa únicamente del color.
 *
 * Todos los valores visuales provienen de `frontend/src/styles/tokens.ts`.
 */

import type { ReactNode } from 'react';
import { AlertTriangle, CheckCircle2, Info } from 'lucide-react';

import { tokens } from '../../styles/tokens';

/** Matices semánticos disponibles para la tarjeta. */
export type TonoClinicalCard = 'default' | 'success' | 'danger' | 'warning' | 'info';

export interface ClinicalCardProps {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  tone?: TonoClinicalCard;
  icon?: ReactNode;
}

/** Descripción textual del matiz, para no comunicar el estado sólo por color. */
const ETIQUETA_TONO: Record<Exclude<TonoClinicalCard, 'default'>, string> = {
  success: 'Resultado favorable',
  danger: 'Hallazgo crítico',
  warning: 'Requiere atención',
  info: 'Información clínica',
};

/** Color de acento de cada matiz semántico. */
const COLOR_TONO: Record<Exclude<TonoClinicalCard, 'default'>, string> = {
  success: tokens.colors.success,
  danger: tokens.colors.danger,
  warning: tokens.colors.warning,
  info: tokens.colors.info,
};

/** Fondo tenue del distintivo de estado de cada matiz. */
const FONDO_TONO: Record<Exclude<TonoClinicalCard, 'default'>, string> = {
  success: tokens.colors.successSubtle,
  danger: tokens.colors.dangerSubtle,
  warning: tokens.colors.warningSubtle,
  info: tokens.colors.primarySubtle,
};

/** Ícono asociado a cada matiz semántico. */
const ICONO_TONO: Record<Exclude<TonoClinicalCard, 'default'>, ReactNode> = {
  success: (
    <CheckCircle2 size={tokens.iconography.sizes.sm} strokeWidth={1.75} aria-hidden="true" />
  ),
  danger: (
    <AlertTriangle size={tokens.iconography.sizes.sm} strokeWidth={1.75} aria-hidden="true" />
  ),
  warning: (
    <AlertTriangle size={tokens.iconography.sizes.sm} strokeWidth={1.75} aria-hidden="true" />
  ),
  info: <Info size={tokens.iconography.sizes.sm} strokeWidth={1.75} aria-hidden="true" />,
};

/**
 * Tarjeta clínica con cabecera opcional y matiz semántico.
 */
export function ClinicalCard({
  title,
  subtitle,
  children,
  tone = 'default',
  icon,
}: ClinicalCardProps) {
  const insignia = tokens.typography.scale.caption;
  const titular = tokens.typography.scale.h3;
  const subtitulo = tokens.typography.scale.bodySmall;
  const conCabecera = Boolean(title || subtitle || icon || tone !== 'default');

  return (
    <section
      className="flex overflow-hidden"
      style={{
        backgroundColor: tokens.colors.surface,
        border: `1px solid ${tokens.colors.border}`,
        borderRadius: tokens.borderRadius.xl,
        boxShadow: tokens.shadows.sm,
      }}
    >
      {tone !== 'default' ? (
        <span
          className="w-1 shrink-0"
          style={{ backgroundColor: COLOR_TONO[tone] }}
          aria-hidden="true"
        />
      ) : null}

      <div className="flex-1 p-5 sm:p-6">
        {conCabecera ? (
          <header className="mb-4 flex items-start justify-between gap-3">
            <div className="flex min-w-0 items-start gap-3">
              {icon ? (
                <span
                  className="shrink-0"
                  style={{ color: tokens.colors.textSecondary }}
                >
                  {icon}
                </span>
              ) : null}

              <div className="min-w-0">
                {title ? (
                  <h2
                    className="truncate"
                    style={{
                      fontSize: titular.size,
                      lineHeight: titular.lineHeight,
                      fontWeight: titular.weight,
                      color: tokens.colors.textPrimary,
                    }}
                  >
                    {title}
                  </h2>
                ) : null}

                {subtitle ? (
                  <p
                    className="mt-1"
                    style={{
                      fontSize: subtitulo.size,
                      lineHeight: subtitulo.lineHeight,
                      color: tokens.colors.textSecondary,
                    }}
                  >
                    {subtitle}
                  </p>
                ) : null}
              </div>
            </div>

            {tone !== 'default' ? (
              <span
                className="inline-flex shrink-0 items-center gap-1.5 px-2.5 py-1"
                style={{
                  backgroundColor: FONDO_TONO[tone],
                  borderRadius: tokens.borderRadius.pill,
                  color: COLOR_TONO[tone],
                  fontSize: insignia.size,
                  lineHeight: insignia.lineHeight,
                  fontWeight: 600,
                  whiteSpace: 'nowrap',
                }}
              >
                {ICONO_TONO[tone]}
                {ETIQUETA_TONO[tone]}
              </span>
            ) : null}
          </header>
        ) : null}

        {children}
      </div>
    </section>
  );
}

export default ClinicalCard;
