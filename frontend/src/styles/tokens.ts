/**
 * Tokens de diseño del proyecto "Pre-screening para Ensayos Clínicos Estado 1".
 *
 * Esta es la única fuente de verdad de color, tipografía, espaciado, radios,
 * sombras, iconografía, movimiento y accesibilidad de la interfaz. Todos los
 * componentes de React deben importar y utilizar estos tokens en lugar de
 * escribir valores CSS literales, de modo que la aplicación se mantenga fiel
 * al contrato de diseño aprobado para el protocolo ALM-PSO-2026.
 *
 * Regla de importación según la ubicación del archivo:
 *   src/*.tsx                → import { tokens } from './styles/tokens'
 *   src/pages/*.tsx          → import { tokens } from '../styles/tokens'
 *   src/components/*.tsx     → import { tokens } from '../styles/tokens'
 *   src/components/ui/*.tsx  → import { tokens } from '../../styles/tokens'
 *   src/hooks/*.ts           → import { tokens } from '../styles/tokens'
 */

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
    overlay: "rgba(13, 27, 42, 0.45)",
  },
  typography: {
    fontFamily: "Inter, system-ui, -apple-system, sans-serif",
    scale: {
      display: {
        size: "30px",
        lineHeight: "38px",
        weight: "700",
      },
      h1: {
        size: "24px",
        lineHeight: "32px",
        weight: "700",
      },
      h2: {
        size: "20px",
        lineHeight: "28px",
        weight: "600",
      },
      h3: {
        size: "16px",
        lineHeight: "24px",
        weight: "600",
      },
      body: {
        size: "16px",
        lineHeight: "24px",
        weight: "400",
      },
      bodySmall: {
        size: "14px",
        lineHeight: "20px",
        weight: "400",
      },
      label: {
        size: "14px",
        lineHeight: "20px",
        weight: "500",
      },
      caption: {
        size: "12px",
        lineHeight: "16px",
        weight: "400",
      },
    },
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
    "10": "64px",
  },
  borderRadius: {
    sm: "6px",
    md: "8px",
    lg: "12px",
    xl: "16px",
    pill: "999px",
  },
  shadows: {
    none: "none",
    sm: "0 1px 2px rgba(13, 27, 42, 0.05)",
    md: "0 4px 12px rgba(13, 27, 42, 0.08)",
    lg: "0 12px 32px rgba(13, 27, 42, 0.12)",
    focus: "0 0 0 3px rgba(14, 94, 158, 0.18)",
  },
  iconography: {
    style: "Lucide React, linear, stroke 1.75px",
    sizes: {
      sm: "16px",
      md: "20px",
      lg: "24px",
      xl: "32px",
    },
    usage:
      "Íconos lineales y descriptivos, nunca decorativos sin contexto. Los estados clínicos usan ícono más punto de color para evitar depender solo del color.",
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
      "El veredicto Elegible/No Elegible aparece con un refuerzo de color pero sin movimiento agresivo.",
    ],
  },
  accessibility: {
    contrast:
      "Contraste AA mínimo en textos y AAA en estado de veredicto y errores.",
    focusVisible: "Anillo de foco visible en todos los controles interactivos.",
    targetSize: "Área mínima de interacción de 44x44px para controles táctiles en tablet.",
    forms:
      "Etiquetas visibles, mensajes de error asociados con aria-live y validación clara antes del envío.",
    semanticStates:
      "El color nunca es el único canal para comunicar elegibilidad o error; siempre se acompaña de texto o ícono.",
  },
} as const;

/** Forma de los tokens de diseño, útil para tipar estilos derivados. */
export type DesignTokens = typeof tokens;
