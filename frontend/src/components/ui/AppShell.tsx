/**
 * Estructura base responsive de la aplicación clínica.
 *
 * `AppShell` compone la cabecera institucional, la navegación lateral
 * colapsable y el área de contenido de las vistas del ensayo ALM-PSO-2026.
 * En tablet e iPad la navegación se colapsa en un cajón superpuesto para
 * priorizar el área de captura de datos; a partir de pantalla grande queda
 * fija junto al contenido.
 *
 * Todos los valores visuales provienen de `frontend/src/styles/tokens.ts`.
 */

import { useEffect, useState, type ReactNode } from 'react';
import {
  BarChart3,
  ClipboardCheck,
  ClipboardList,
  Lock,
  Menu,
  Scale,
  ShieldCheck,
  X,
} from 'lucide-react';

import { tokens } from '../../styles/tokens';

/** Roles clínicos habilitados para operar el ensayo. */
export type RolClinico = 'investigador' | 'gestor';

/** Identificadores de las vistas clínicas registradas en el enrutamiento. */
export type IdVistaClinica =
  | 'inicio'
  | 'formulario'
  | 'resultado'
  | 'auditoria'
  | 'reclutamiento'
  | 'acceso';

export interface AppShellProps {
  children: ReactNode;
  role: RolClinico;
  activeView: string;
  onNavigate: (view: string) => void;
}

interface EntradaNavegacion {
  id: IdVistaClinica;
  nombre: string;
  roles: RolClinico[];
  icono: ReactNode;
}

const PROTOCOLO_CODIGO = 'ALM-PSO-2026';
const PROTOCOLO_TITULO = 'Ensayo clínico de psoriasis en placas';
const APLICACION_NOMBRE = 'Pre-screening para Ensayos Clínicos Estado 1';

const NAVEGACION: EntradaNavegacion[] = [
  {
    id: 'inicio',
    nombre: 'Centro de evaluaciones',
    roles: ['investigador', 'gestor'],
    icono: <ClipboardCheck size={20} strokeWidth={1.75} aria-hidden="true" />,
  },
  {
    id: 'formulario',
    nombre: 'Formulario de evaluación clínica',
    roles: ['investigador', 'gestor'],
    icono: <ClipboardList size={20} strokeWidth={1.75} aria-hidden="true" />,
  },
  {
    id: 'resultado',
    nombre: 'Resolución de elegibilidad',
    roles: ['investigador', 'gestor'],
    icono: <Scale size={20} strokeWidth={1.75} aria-hidden="true" />,
  },
  {
    id: 'auditoria',
    nombre: 'Auditoría y trazabilidad',
    roles: ['investigador', 'gestor'],
    icono: <ShieldCheck size={20} strokeWidth={1.75} aria-hidden="true" />,
  },
  {
    id: 'reclutamiento',
    nombre: 'Panel de reclutamiento',
    roles: ['gestor'],
    icono: <BarChart3 size={20} strokeWidth={1.75} aria-hidden="true" />,
  },
  {
    id: 'acceso',
    nombre: 'Acceso seguro',
    roles: ['investigador', 'gestor'],
    icono: <Lock size={20} strokeWidth={1.75} aria-hidden="true" />,
  },
];

/** Etiqueta legible del rol con el que opera el usuario. */
const ETIQUETA_ROL: Record<RolClinico, string> = {
  investigador: 'Investigador clínico',
  gestor: 'Gestor del ensayo',
};

/**
 * Estructura base de la aplicación: cabecera clínica, navegación lateral
 * colapsable y área de contenido.
 */
export function AppShell({
  children,
  role,
  activeView,
  onNavigate,
}: AppShellProps) {
  const [cajonAbierto, setCajonAbierto] = useState(false);
  const insignia = tokens.typography.scale.caption;
  const rotulo = tokens.typography.scale.label;
  const titular = tokens.typography.scale.h3;

  useEffect(() => {
    setCajonAbierto(false);
  }, [activeView]);

  const vistasPermitidas = NAVEGACION.filter((vista) => vista.roles.includes(role));

  const navegar = (vista: IdVistaClinica) => {
    setCajonAbierto(false);
    onNavigate(vista);
  };

  return (
    <div
      className="flex min-h-screen flex-col"
      style={{
        backgroundColor: tokens.colors.background,
        color: tokens.colors.textPrimary,
        fontFamily: tokens.typography.fontFamily,
      }}
    >
      <a href="#contenido-app-shell" className="skip-link no-print">
        Saltar al contenido principal
      </a>

      <header
        className="no-print sticky top-0 z-30 border-b"
        style={{
          backgroundColor: tokens.colors.surface,
          borderColor: tokens.colors.border,
          boxShadow: tokens.shadows.sm,
        }}
      >
        <div className="mx-auto flex w-full max-w-7xl items-center gap-3 px-4 py-3 sm:px-6 lg:px-8">
          <button
            type="button"
            onClick={() => setCajonAbierto((abierto) => !abierto)}
            aria-expanded={cajonAbierto}
            aria-controls="navegacion-app-shell"
            className="inline-flex h-11 w-11 shrink-0 items-center justify-center lg:hidden"
            style={{
              border: `1px solid ${tokens.colors.border}`,
              borderRadius: tokens.borderRadius.md,
              backgroundColor: tokens.colors.surface,
              color: tokens.colors.textSecondary,
            }}
          >
            {cajonAbierto ? (
              <X size={20} strokeWidth={1.75} aria-hidden="true" />
            ) : (
              <Menu size={20} strokeWidth={1.75} aria-hidden="true" />
            )}
            <span className="visually-hidden">
              {cajonAbierto ? 'Cerrar navegación' : 'Abrir navegación'}
            </span>
          </button>

          <div className="flex min-w-0 flex-1 flex-col">
            <p
              className="truncate"
              style={{
                fontSize: rotulo.size,
                lineHeight: rotulo.lineHeight,
                fontWeight: rotulo.weight,
                color: tokens.colors.textTertiary,
              }}
            >
              {APLICACION_NOMBRE}
            </p>
            <p
              className="truncate"
              style={{
                fontSize: titular.size,
                lineHeight: titular.lineHeight,
                fontWeight: titular.weight,
                color: tokens.colors.textPrimary,
              }}
            >
              Motor de Pre-selección Clínica Inteligente
            </p>
          </div>

          <span
            className="hidden shrink-0 items-center gap-2 px-3 py-1 sm:inline-flex"
            style={{
              backgroundColor: tokens.colors.primarySubtle,
              borderRadius: tokens.borderRadius.pill,
              color: tokens.colors.primary,
              fontSize: insignia.size,
              lineHeight: insignia.lineHeight,
              fontWeight: 600,
            }}
          >
            <span
              className="h-2 w-2"
              style={{
                backgroundColor: tokens.colors.primary,
                borderRadius: tokens.borderRadius.pill,
              }}
              aria-hidden="true"
            />
            Protocolo {PROTOCOLO_CODIGO}
          </span>

          <span
            className="hidden shrink-0 px-3 py-1 md:inline-flex"
            style={{
              border: `1px solid ${tokens.colors.border}`,
              borderRadius: tokens.borderRadius.pill,
              color: tokens.colors.textSecondary,
              fontSize: insignia.size,
              lineHeight: insignia.lineHeight,
              fontWeight: 600,
            }}
          >
            {ETIQUETA_ROL[role]}
          </span>
        </div>
      </header>

      <div className="flex flex-1 flex-col lg:flex-row">
        {cajonAbierto ? (
          <div
            className="no-print fixed inset-0 z-20 lg:hidden"
            style={{ backgroundColor: tokens.colors.overlay }}
            onClick={() => setCajonAbierto(false)}
            aria-hidden="true"
          />
        ) : null}

        <nav
          id="navegacion-app-shell"
          aria-label="Navegación principal"
          className={`clinical-scroll no-print fixed inset-y-0 left-0 z-30 w-72 overflow-y-auto border-r px-4 py-5 lg:static lg:block lg:shrink-0 lg:px-0 lg:py-0 ${
            cajonAbierto ? 'block' : 'hidden'
          }`}
          style={{
            backgroundColor: tokens.colors.surface,
            borderColor: tokens.colors.border,
          }}
        >
          <div className="mb-4 flex items-center gap-2 px-3">
            <span
              className="h-2 w-2"
              style={{
                backgroundColor: tokens.colors.success,
                borderRadius: tokens.borderRadius.pill,
              }}
              aria-hidden="true"
            />
            <p
              style={{
                fontSize: insignia.size,
                lineHeight: insignia.lineHeight,
                fontWeight: 600,
                color: tokens.colors.textSecondary,
              }}
            >
              Protocolo {PROTOCOLO_CODIGO}
            </p>
          </div>

          <p
            className="px-3"
            style={{
              fontSize: insignia.size,
              lineHeight: insignia.lineHeight,
              color: tokens.colors.textTertiary,
            }}
          >
            {PROTOCOLO_TITULO}
          </p>

          <ul className="mt-2 flex flex-col gap-1">
            {vistasPermitidas.map((vista) => {
              const activa = vista.id === activeView;
              return (
                <li key={vista.id}>
                  <button
                    type="button"
                    onClick={() => navegar(vista.id)}
                    aria-current={activa ? 'page' : undefined}
                    className={`flex w-full items-center gap-3 px-3 py-3 text-left ${
                      activa ? '' : 'hover:bg-[var(--color-surface-alt)]'
                    }`}
                    style={{
                      borderLeft: `3px solid ${
                        activa ? tokens.colors.primary : 'transparent'
                      }`,
                      borderRadius: tokens.borderRadius.md,
                      backgroundColor: activa
                        ? tokens.colors.primarySubtle
                        : 'transparent',
                      color: activa
                        ? tokens.colors.primaryHover
                        : tokens.colors.textSecondary,
                      fontSize: rotulo.size,
                      lineHeight: rotulo.lineHeight,
                      fontWeight: activa ? 600 : rotulo.weight,
                      transition: `background-color ${tokens.motion.durationFast} ${tokens.motion.easing}, color ${tokens.motion.durationFast} ${tokens.motion.easing}`,
                    }}
                  >
                    {vista.icono}
                    <span className="flex-1">{vista.nombre}</span>
                  </button>
                </li>
              );
            })}
          </ul>

          <div
            className="mt-6 border p-3"
            style={{
              borderColor: tokens.colors.border,
              borderRadius: tokens.borderRadius.md,
              backgroundColor: tokens.colors.surfaceAlt,
            }}
          >
            <p
              style={{
                fontSize: insignia.size,
                lineHeight: insignia.lineHeight,
                color: tokens.colors.textSecondary,
              }}
            >
              Cumplimiento GxP: cada evaluación queda registrada en el audit
              trail con hash encadenado, de modo que cualquier alteración
              posterior resulta detectable.
            </p>
          </div>
        </nav>

        <main
          id="contenido-app-shell"
          tabIndex={-1}
          className="flex-1 px-4 py-6 sm:px-6 lg:px-8 lg:py-8"
        >
          <div className="mx-auto w-full max-w-6xl">{children}</div>
        </main>
      </div>
    </div>
  );
}

export default AppShell;
