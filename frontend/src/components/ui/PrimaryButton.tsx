/**
 * Botón de acción principal del flujo clínico.
 *
 * Es el componente CTA del ensayo: iniciar una evaluación, confirmar el envío
 * de datos clínicos o volver al flujo de trabajo. Mantiene un área táctil
 * mínima de 44 px y un estado de carga que evita el doble envío mientras el
 * motor de reglas resuelve el veredicto.
 *
 * Todos los valores visuales provienen de `frontend/src/styles/tokens.ts`.
 */

import type { MouseEventHandler, ReactNode } from 'react';
import { Loader2 } from 'lucide-react';

import { tokens } from '../../styles/tokens';

/** Variantes visuales disponibles para el botón. */
export type VarianteBoton = 'primary' | 'secondary' | 'danger' | 'ghost';

/** Tamaños disponibles para el botón. */
export type TamanoBoton = 'sm' | 'md' | 'lg';

export interface PrimaryButtonProps {
  label: string;
  onClick: MouseEventHandler<HTMLButtonElement>;
  variant?: VarianteBoton;
  size?: TamanoBoton;
  icon?: ReactNode;
  disabled?: boolean;
  loading?: boolean;
}

/** Estilos de superficie, texto y borde por variante. */
const ESTILOS_VARIANTE: Record<
  VarianteBoton,
  { fondo: string; texto: string; borde: string; hover: string }
> = {
  primary: {
    fondo: tokens.colors.primary,
    texto: tokens.colors.surface,
    borde: tokens.colors.primary,
    hover: 'hover:bg-[var(--color-primary-hover)]',
  },
  secondary: {
    fondo: tokens.colors.surface,
    texto: tokens.colors.textPrimary,
    borde: tokens.colors.borderStrong,
    hover: 'hover:bg-[var(--color-surface-alt)]',
  },
  danger: {
    fondo: tokens.colors.danger,
    texto: tokens.colors.surface,
    borde: tokens.colors.danger,
    hover: 'hover:opacity-90',
  },
  ghost: {
    fondo: 'transparent',
    texto: tokens.colors.primary,
    borde: 'transparent',
    hover: 'hover:bg-[var(--color-surface-alt)]',
  },
};

/** Alturas, espaciado y tipografía por tamaño. */
const ESTILOS_TAMANO: Record<
  TamanoBoton,
  { altura: string; padding: string; tamano: string; lineHeight: string; peso: number }
> = {
  sm: {
    altura: 'min-h-[44px]',
    padding: 'px-3',
    tamano: tokens.typography.scale.label.size,
    lineHeight: tokens.typography.scale.label.lineHeight,
    peso: 600,
  },
  md: {
    altura: 'min-h-[48px]',
    padding: 'px-4',
    tamano: tokens.typography.scale.body.size,
    lineHeight: tokens.typography.scale.body.lineHeight,
    peso: 600,
  },
  lg: {
    altura: 'min-h-[56px]',
    padding: 'px-6',
    tamano: tokens.typography.scale.h3.size,
    lineHeight: tokens.typography.scale.h3.lineHeight,
    peso: 600,
  },
};

/**
 * Botón de acción principal con estados de carga y deshabilitado.
 */
export function PrimaryButton({
  label,
  onClick,
  variant = 'primary',
  size = 'md',
  icon,
  disabled = false,
  loading = false,
}: PrimaryButtonProps) {
  const estilosVariante = ESTILOS_VARIANTE[variant];
  const estilosTamano = ESTILOS_TAMANO[size];
  const bloqueado = disabled || loading;

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={bloqueado}
      aria-busy={loading}
      aria-disabled={bloqueado}
      className={`inline-flex ${estilosTamano.altura} ${estilosTamano.padding} items-center justify-center gap-2 disabled:cursor-not-allowed disabled:opacity-60 ${estilosVariante.hover}`}
      style={{
        backgroundColor: estilosVariante.fondo,
        color: estilosVariante.texto,
        border: `1px solid ${estilosVariante.borde}`,
        borderRadius: tokens.borderRadius.md,
        fontSize: estilosTamano.tamano,
        lineHeight: estilosTamano.lineHeight,
        fontWeight: estilosTamano.peso,
        boxShadow: variant === 'primary' ? tokens.shadows.sm : tokens.shadows.none,
        transition: `background-color ${tokens.motion.durationFast} ${tokens.motion.easing}, box-shadow ${tokens.motion.durationFast} ${tokens.motion.easing}`,
      }}
    >
      {loading ? (
        <Loader2
          size={tokens.iconography.sizes.sm}
          strokeWidth={1.75}
          className="animate-spin"
          aria-hidden="true"
        />
      ) : (
        icon
      )}
      <span>{label}</span>
    </button>
  );
}

export default PrimaryButton;
