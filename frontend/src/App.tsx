/**
 * Componente principal de la aplicación y enrutamiento.
 *
 * Define la estructura clínica de navegación del ensayo ALM-PSO-2026: cabecera
 * con el protocolo activo, lateral colapsable para tablet/iPad y enrutamiento
 * de las vistas del contrato UI/UX.
 *
 * Todos los valores visuales provienen de `frontend/src/styles/tokens.ts`, de
 * modo que ningún componente escriba colores, tipografías, radios o sombras
 * literales. Las páginas funcionales de cada vista se incorporan en los
 * entregables posteriores del plan de desarrollo, sustituyendo el elemento de
 * ruta correspondiente por el componente de página del contrato.
 */

import { useEffect, useState, type ReactNode } from 'react';
import {
  BarChart3,
  ChevronRight,
  ClipboardCheck,
  ClipboardList,
  Lock,
  Menu,
  Scale,
  ShieldCheck,
  X,
} from 'lucide-react';
import {
  BrowserRouter,
  Link,
  Outlet,
  Route,
  Routes,
  useLocation,
} from 'react-router-dom';

import { tokens } from './styles/tokens';

const APLICACION_NOMBRE = 'Pre-screening para Ensayos Clínicos Estado 1';
const PROTOCOLO_CODIGO = 'ALM-PSO-2026';
const PROTOCOLO_TITULO = 'Ensayo clínico de psoriasis en placas';

/** Roles clínicos habilitados para operar el ensayo. */
type RolClinico = 'investigador' | 'gestor';

/** Vista clínica del contrato UI/UX registrada en el enrutamiento. */
interface VistaClinica {
  id: string;
  ruta: string;
  nombre: string;
  proposito: string;
  secciones: string[];
  roles: RolClinico[];
  icono: ReactNode;
}

const VISTAS: VistaClinica[] = [
  {
    id: 'inicio',
    ruta: '/',
    nombre: 'Centro de evaluaciones',
    proposito:
      'Punto de entrada operativo que permite iniciar una nueva evaluación y revisar evaluaciones recientes con su estado y trazabilidad.',
    secciones: [
      'Encabezado del protocolo ALM-PSO-2026',
      'Métricas rápidas del flujo',
      'Lista de evaluaciones recientes',
      'Acción principal de nueva evaluación',
    ],
    roles: ['investigador', 'gestor'],
    icono: <ClipboardCheck size={20} strokeWidth={1.75} aria-hidden="true" />,
  },
  {
    id: 'formulario',
    ruta: '/evaluacion',
    nombre: 'Formulario de Evaluación Clínica',
    proposito:
      'Capturar de forma ágil y validada los datos demográficos y clínicos del paciente para ejecutar la evaluación de elegibilidad.',
    secciones: [
      'Identificación enmascarada del paciente',
      'Datos demográficos',
      'Criterios clínicos PASI y BSA',
      'Criterios de exclusión',
      'Revisión y activación de la evaluación',
    ],
    roles: ['investigador', 'gestor'],
    icono: <ClipboardList size={20} strokeWidth={1.75} aria-hidden="true" />,
  },
  {
    id: 'resultado',
    ruta: '/resultado',
    nombre: 'Resolución de Elegibilidad',
    proposito:
      'Mostrar el veredicto inmediato y el desglose de criterios cumplidos y bloqueantes, con soporte para audit trail clínico.',
    secciones: [
      'Veredicto principal',
      'Resumen enmascarado del paciente',
      'Criterios de inclusión evaluados',
      'Criterios de exclusión evaluados',
      'Detalle de reglas de la decisión',
    ],
    roles: ['investigador', 'gestor'],
    icono: <Scale size={20} strokeWidth={1.75} aria-hidden="true" />,
  },
  {
    id: 'auditoria',
    ruta: '/auditoria',
    nombre: 'Auditoría y trazabilidad',
    proposito:
      'Revisar el historial de evaluaciones, usuarios responsables y reglas exactas que motivaron cada rechazo, cumpliendo requisitos GxP.',
    secciones: [
      'Filtros de auditoría',
      'Línea de evaluaciones',
      'Detalle de reglas aplicadas',
      'Estado de integridad del audit trail',
    ],
    roles: ['investigador', 'gestor'],
    icono: <ShieldCheck size={20} strokeWidth={1.75} aria-hidden="true" />,
  },
  {
    id: 'reclutamiento',
    ruta: '/reclutamiento',
    nombre: 'Panel de reclutamiento',
    proposito:
      'Seguir el rendimiento del reclutamiento con los totales de elegibles y no elegibles del protocolo y los motivos de rechazo más frecuentes.',
    secciones: [
      'Totales de elegibles y no elegibles',
      'Motivos de rechazo más frecuentes',
      'Tendencia de evaluaciones por periodo',
    ],
    roles: ['gestor'],
    icono: <BarChart3 size={20} strokeWidth={1.75} aria-hidden="true" />,
  },
  {
    id: 'acceso',
    ruta: '/acceso',
    nombre: 'Acceso seguro',
    proposito:
      'Permitir la identificación del investigador clínico o gestor del ensayo para garantizar trazabilidad de cada evaluación y proteger datos sensibles.',
    secciones: [
      'Identificación institucional',
      'Inicio de sesión',
      'Aviso de privacidad y cumplimiento GxP',
    ],
    roles: ['investigador', 'gestor'],
    icono: <Lock size={20} strokeWidth={1.75} aria-hidden="true" />,
  },
];

/** Obtiene una vista registrada en el contrato por su identificador. */
function obtenerVista(id: string): VistaClinica {
  const vista = VISTAS.find((item) => item.id === id);
  if (!vista) {
    throw new Error(`Vista clínica no registrada en el enrutamiento: ${id}`);
  }
  return vista;
}

/** Indica si la vista corresponde a la ruta mostrada en ese momento. */
function esVistaActiva(vista: VistaClinica, rutaActual: string): boolean {
  if (vista.id === 'resultado') {
    return rutaActual === '/resultado' || rutaActual.endsWith('/resultado');
  }
  if (vista.id === 'formulario') {
    return (
      rutaActual === '/evaluacion' ||
      (rutaActual.startsWith('/evaluacion/') && !rutaActual.endsWith('/resultado'))
    );
  }
  return rutaActual === vista.ruta;
}

interface CabeceraClinicaProps {
  menuAbierto: boolean;
  onAlternarMenu: () => void;
}

/** Cabecera clínica con el protocolo activo y el control del lateral. */
function CabeceraClinica({ menuAbierto, onAlternarMenu }: CabeceraClinicaProps) {
  const rotulo = tokens.typography.scale.label;
  const titulo = tokens.typography.scale.h3;
  const insignia = tokens.typography.scale.caption;

  return (
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
          onClick={onAlternarMenu}
          aria-expanded={menuAbierto}
          aria-controls="navegacion-principal"
          className="inline-flex h-11 w-11 shrink-0 items-center justify-center lg:hidden"
          style={{
            border: `1px solid ${tokens.colors.border}`,
            borderRadius: tokens.borderRadius.md,
            backgroundColor: tokens.colors.surface,
            color: tokens.colors.textSecondary,
          }}
        >
          {menuAbierto ? (
            <X size={20} strokeWidth={1.75} aria-hidden="true" />
          ) : (
            <Menu size={20} strokeWidth={1.75} aria-hidden="true" />
          )}
          <span className="visually-hidden">
            {menuAbierto ? 'Cerrar navegación' : 'Abrir navegación'}
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
              fontSize: titulo.size,
              lineHeight: titulo.lineHeight,
              fontWeight: titulo.weight,
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
      </div>
    </header>
  );
}

interface NavegacionClinicaProps {
  abierta: boolean;
  onCerrar: () => void;
}

/** Navegación lateral colapsable con las vistas del contrato UI/UX. */
function NavegacionClinica({ abierta, onCerrar }: NavegacionClinicaProps) {
  const insignia = tokens.typography.scale.caption;
  const ubicacion = useLocation();

  return (
    <>
      {abierta ? (
        <div
          className="no-print fixed inset-0 z-20 lg:hidden"
          style={{ backgroundColor: tokens.colors.overlay }}
          onClick={onCerrar}
          aria-hidden="true"
        />
      ) : null}

      <nav
        id="navegacion-principal"
        aria-label="Navegación principal"
        className={`clinical-scroll no-print fixed inset-y-0 left-0 z-30 w-72 overflow-y-auto border-r px-4 py-5 lg:static lg:block lg:shrink-0 lg:px-0 lg:py-0 ${
          abierta ? 'block' : 'hidden'
        }`}
        style={{ backgroundColor: tokens.colors.surface, borderColor: tokens.colors.border }}
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

        <ul className="flex flex-col gap-1">
          {VISTAS.map((vista) => {
            const activa = esVistaActiva(vista, ubicacion.pathname);
            return (
              <li key={vista.id}>
                <Link
                  to={vista.ruta}
                  aria-current={activa ? 'page' : undefined}
                  className="flex items-center gap-3 px-3 py-3"
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
                    fontSize: tokens.typography.scale.label.size,
                    lineHeight: tokens.typography.scale.label.lineHeight,
                    fontWeight: activa
                      ? 600
                      : tokens.typography.scale.label.weight,
                    transition: `background-color ${tokens.motion.durationFast} ${tokens.motion.easing}, color ${tokens.motion.durationFast} ${tokens.motion.easing}`,
                  }}
                >
                  {vista.icono}
                  <span className="flex-1">{vista.nombre}</span>
                  <ChevronRight size={16} strokeWidth={1.75} aria-hidden="true" />
                </Link>
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
            Cumplimiento GxP: cada evaluación queda registrada en el audit trail
            con hash encadenado, de modo que cualquier alteración posterior es
            detectable.
          </p>
        </div>
      </nav>
    </>
  );
}

interface VistaContenidoProps {
  vista: VistaClinica;
}

/** Contenido de una vista: propósito, secciones contractuales y aviso GxP. */
function VistaContenido({ vista }: VistaContenidoProps) {
  const rotulo = tokens.typography.scale.caption;
  const titular = tokens.typography.scale.h1;
  const cuerpo = tokens.typography.scale.body;
  const cuerpoPequeno = tokens.typography.scale.bodySmall;
  const subtitulo = tokens.typography.scale.h3;

  return (
    <div className="flex flex-col gap-6">
      <section
        className="border p-5 sm:p-6"
        style={{
          backgroundColor: tokens.colors.surface,
          borderColor: tokens.colors.border,
          borderRadius: tokens.borderRadius.xl,
          boxShadow: tokens.shadows.sm,
        }}
      >
        <span
          className="inline-flex items-center gap-2 px-3 py-1"
          style={{
            backgroundColor: tokens.colors.primarySubtle,
            borderRadius: tokens.borderRadius.pill,
            color: tokens.colors.primary,
            fontSize: rotulo.size,
            lineHeight: rotulo.lineHeight,
            fontWeight: 600,
          }}
        >
          {vista.icono}
          Acceso: {vista.roles.join(' · ')}
        </span>

        <h1
          className="mt-3"
          style={{
            fontSize: titular.size,
            lineHeight: titular.lineHeight,
            fontWeight: titular.weight,
            color: tokens.colors.textPrimary,
          }}
        >
          {vista.nombre}
        </h1>

        <p
          className="mt-2"
          style={{
            fontSize: cuerpo.size,
            lineHeight: cuerpo.lineHeight,
            color: tokens.colors.textSecondary,
          }}
        >
          {vista.proposito}
        </p>

        <p
          className="mt-3"
          style={{
            fontSize: rotulo.size,
            lineHeight: rotulo.lineHeight,
            color: tokens.colors.textTertiary,
          }}
        >
          Protocolo {PROTOCOLO_CODIGO} · {PROTOCOLO_TITULO}
        </p>
      </section>

      <section
        aria-label="Secciones de la vista"
        className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3"
      >
        {vista.secciones.map((seccion, indice) => (
          <article
            key={seccion}
            className="border p-4"
            style={{
              backgroundColor: tokens.colors.surface,
              borderColor: tokens.colors.border,
              borderRadius: tokens.borderRadius.lg,
              boxShadow: tokens.shadows.sm,
            }}
          >
            <p
              style={{
                fontSize: rotulo.size,
                lineHeight: rotulo.lineHeight,
                fontWeight: 600,
                color: tokens.colors.textTertiary,
              }}
            >
              Sección {indice + 1} de {vista.secciones.length}
            </p>
            <h2
              className="mt-1"
              style={{
                fontSize: subtitulo.size,
                lineHeight: subtitulo.lineHeight,
                fontWeight: subtitulo.weight,
                color: tokens.colors.textPrimary,
              }}
            >
              {seccion}
            </h2>
          </article>
        ))}
      </section>

      <aside
        className="border p-4"
        style={{
          backgroundColor: tokens.colors.surfaceAlt,
          borderColor: tokens.colors.border,
          borderRadius: tokens.borderRadius.md,
        }}
      >
        <p
          style={{
            fontSize: cuerpoPequeno.size,
            lineHeight: cuerpoPequeno.lineHeight,
            color: tokens.colors.textSecondary,
          }}
        >
          Los datos clínicos de esta vista se consultan mediante la API interna
          del ensayo y se presentan siempre con los campos de identificación
          personal enmascarados, conforme a los requisitos de privacidad
          clínica (GDPR/HIPAA).
        </p>
      </aside>
    </div>
  );
}

/** Vista mostrada cuando la ruta solicitada no existe en la aplicación. */
function RutaNoEncontrada() {
  const titular = tokens.typography.scale.h2;
  const cuerpo = tokens.typography.scale.body;

  return (
    <section
      className="border p-8 text-center"
      style={{
        backgroundColor: tokens.colors.surface,
        borderColor: tokens.colors.border,
        borderRadius: tokens.borderRadius.xl,
        boxShadow: tokens.shadows.sm,
      }}
    >
      <h1
        style={{
          fontSize: titular.size,
          lineHeight: titular.lineHeight,
          fontWeight: titular.weight,
          color: tokens.colors.textPrimary,
        }}
      >
        Página no encontrada
      </h1>
      <p
        className="mt-2"
        style={{
          fontSize: cuerpo.size,
          lineHeight: cuerpo.lineHeight,
          color: tokens.colors.textSecondary,
        }}
      >
        La ruta solicitada no corresponde a ninguna vista de la aplicación de
        pre-selección clínica.
      </p>
      <Link
        to="/"
        className="mt-6 inline-flex min-h-[44px] items-center justify-center px-4"
        style={{
          backgroundColor: tokens.colors.primary,
          borderRadius: tokens.borderRadius.md,
          color: tokens.colors.surface,
          fontSize: tokens.typography.scale.label.size,
          lineHeight: tokens.typography.scale.label.lineHeight,
          fontWeight: 600,
          transition: `background-color ${tokens.motion.durationFast} ${tokens.motion.easing}`,
        }}
      >
        Volver al Centro de evaluaciones
      </Link>
    </section>
  );
}

/** Estructura base de la aplicación: cabecera, lateral y área de contenido. */
function MarcoClinico() {
  const [menuAbierto, setMenuAbierto] = useState(false);
  const ubicacion = useLocation();

  useEffect(() => {
    setMenuAbierto(false);
  }, [ubicacion.pathname]);

  return (
    <div
      className="flex min-h-screen flex-col"
      style={{
        backgroundColor: tokens.colors.background,
        color: tokens.colors.textPrimary,
        fontFamily: tokens.typography.fontFamily,
      }}
    >
      <a href="#contenido-principal" className="skip-link no-print">
        Saltar al contenido principal
      </a>

      <CabeceraClinica
        menuAbierto={menuAbierto}
        onAlternarMenu={() => setMenuAbierto((abierto) => !abierto)}
      />

      <div className="flex flex-1 flex-col lg:flex-row">
        <NavegacionClinica
          abierta={menuAbierto}
          onCerrar={() => setMenuAbierto(false)}
        />

        <main
          id="contenido-principal"
          tabIndex={-1}
          className="flex-1 px-4 py-6 sm:px-6 lg:px-8 lg:py-8"
        >
          <div className="mx-auto w-full max-w-6xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

/** Enrutamiento de las vistas clínicas del ensayo. */
function Enrutamiento() {
  return (
    <Routes>
      <Route element={<MarcoClinico />}>
        <Route path="/" element={<VistaContenido vista={obtenerVista('inicio')} />} />
        <Route
          path="/evaluacion"
          element={<VistaContenido vista={obtenerVista('formulario')} />}
        />
        <Route
          path="/resultado"
          element={<VistaContenido vista={obtenerVista('resultado')} />}
        />
        <Route
          path="/evaluacion/:evaluacionId/resultado"
          element={<VistaContenido vista={obtenerVista('resultado')} />}
        />
        <Route
          path="/auditoria"
          element={<VistaContenido vista={obtenerVista('auditoria')} />}
        />
        <Route
          path="/reclutamiento"
          element={<VistaContenido vista={obtenerVista('reclutamiento')} />}
        />
        <Route
          path="/acceso"
          element={<VistaContenido vista={obtenerVista('acceso')} />}
        />
        <Route path="*" element={<RutaNoEncontrada />} />
      </Route>
    </Routes>
  );
}

/** Raíz de la aplicación: enrutador y estructura clínica. */
export default function App() {
  return (
    <BrowserRouter>
      <Enrutamiento />
    </BrowserRouter>
  );
}
