/**
 * Campo de formulario clínico con etiqueta, validación y unidad de medida.
 *
 * El componente cubre los controles de datos del protocolo ALM-PSO-2026
 * (texto, numérico, fecha, lista desplegable y confirmaciones binarias) y
 * admite el enmascarado de PII: cuando el campo se marca como `masked`, la
 * interfaz muestra únicamente una versión enmascarada del valor y el dato en
 * claro nunca llega a la pantalla, conforme a los requisitos de privacidad
 * clínica (GDPR/HIPAA).
 *
 * Todos los valores visuales provienen de `frontend/src/styles/tokens.ts`.
 */

import { useId, type ChangeEvent, type ReactNode } from 'react';
import { AlertCircle, ChevronDown, EyeOff } from 'lucide-react';

import { tokens } from '../../styles/tokens';

/** Tipos de control admitidos por el campo clínico. */
export type TipoCampoClinico = 'text' | 'number' | 'select' | 'date' | 'boolean';

/** Opción seleccionable en los campos de tipo lista desplegable. */
export interface OpcionCampoClinico {
  value: string | number;
  label: string;
}

export interface ClinicalFieldProps {
  label: string;
  value: string | number | boolean;
  onChange: (value: string | number | boolean) => void;
  type?: TipoCampoClinico;
  unit?: string;
  error?: string;
  disabled?: boolean;
  masked?: boolean;
  options?: OpcionCampoClinico[];
}

/** Carácter empleado para ocultar los caracteres enmascarados. */
const CARACTER_ENMASCARADO = '•';

/**
 * Enmascara un valor conservando únicamente los dos primeros y los dos
 * últimos caracteres, con la misma política que aplica el backend en
 * `backend/shared/utils.py`.
 */
function enmascararValor(valor: string | number | boolean): string {
  const texto = String(valor);

  if (texto.length === 0) {
    return '';
  }

  if (texto.length <= 4) {
    return CARACTER_ENMASCARADO.repeat(texto.length);
  }

  return `${texto.slice(0, 2)}${CARACTER_ENMASCARADO.repeat(
    texto.length - 4,
  )}${texto.slice(-2)}`;
}

/**
 * Campo de entrada de datos clínicos con soporte de enmascarado de PII.
 */
export function ClinicalField({
  label,
  value,
  onChange,
  type = 'text',
  unit,
  error,
  disabled = false,
  masked = false,
  options,
}: ClinicalFieldProps) {
  const idCampo = useId();
  const idEtiqueta = `${idCampo}-etiqueta`;
  const idError = `${idCampo}-error`;
  const idAyuda = `${idCampo}-ayuda`;

  const rotulo = tokens.typography.scale.label;
  const cuerpo = tokens.typography.scale.bodySmall;
  const insignia = tokens.typography.scale.caption;

  const colorBorde = error
    ? tokens.colors.danger
    : disabled
      ? tokens.colors.border
      : tokens.colors.borderStrong;

  const descripciones = [error ? idError : null, masked ? idAyuda : null]
    .filter(Boolean)
    .join(' ');

  const opcionSeleccionada = options?.find(
    (opcion) => String(opcion.value) === String(value),
  );

  const valorControl = typeof value === 'boolean' ? String(value) : value;

  const manejarCambio = (evento: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const bruto = evento.target.value;

    if (type === 'number') {
      if (bruto === '') {
        onChange('');
        return;
      }

      const numerico = Number(bruto);
      onChange(Number.isFinite(numerico) ? numerico : bruto);
      return;
    }

    if (type === 'select') {
      const encontrada = options?.find(
        (opcion) => String(opcion.value) === bruto,
      );
      onChange(encontrada ? encontrada.value : bruto);
      return;
    }

    onChange(bruto);
  };

  const marcoControl = (className: string, contenido: ReactNode): ReactNode => (
    <div
      className={`flex items-center border focus-within:border-[var(--color-primary)] focus-within:shadow-[var(--shadow-focus)] ${className}`}
      style={{
        borderColor: colorBorde,
        backgroundColor: disabled
          ? tokens.colors.surfaceAlt
          : tokens.colors.surface,
        borderRadius: tokens.borderRadius.md,
      }}
    >
      {contenido}
    </div>
  );

  const renderControl = (): ReactNode => {
    if (masked) {
      const textoEnmascarado =
        type === 'select'
          ? (opcionSeleccionada?.label ?? '')
          : type === 'boolean'
            ? value
              ? 'Sí'
              : 'No'
            : enmascararValor(value);

      return marcoControl(
        '',
        <div className="flex min-h-[44px] flex-1 items-center gap-2 px-3 py-2">
          <EyeOff
            size={tokens.iconography.sizes.sm}
            strokeWidth={1.75}
            style={{ color: tokens.colors.textTertiary }}
            aria-hidden="true"
          />
          <span
            className="font-medium"
            style={{
              fontSize: rotulo.size,
              lineHeight: rotulo.lineHeight,
              color: tokens.colors.textPrimary,
            }}
          >
            {textoEnmascarado}
          </span>
        </div>,
      );
    }

    if (type === 'boolean') {
      const booleano = Boolean(value);

      return (
        <div
          role="group"
          aria-labelledby={idEtiqueta}
          aria-describedby={descripciones || undefined}
          aria-invalid={error ? true : undefined}
          className="flex flex-wrap gap-2"
        >
          {[true, false].map((opcion) => {
            const seleccionada = booleano === opcion;

            return (
              <label
                key={String(opcion)}
                className={`inline-flex min-h-[44px] cursor-pointer items-center gap-2 border px-3 ${
                  disabled ? 'cursor-not-allowed opacity-60' : ''
                }`}
                style={{
                  borderColor: seleccionada
                    ? tokens.colors.primary
                    : tokens.colors.borderStrong,
                  backgroundColor: seleccionada
                    ? tokens.colors.primarySubtle
                    : tokens.colors.surface,
                  borderRadius: tokens.borderRadius.md,
                  fontSize: rotulo.size,
                  lineHeight: rotulo.lineHeight,
                  fontWeight: 500,
                  color: seleccionada
                    ? tokens.colors.primaryHover
                    : tokens.colors.textSecondary,
                }}
              >
                <input
                  type="radio"
                  name={idCampo}
                  value={String(opcion)}
                  checked={seleccionada}
                  disabled={disabled}
                  onChange={() => onChange(opcion)}
                />
                {opcion ? 'Sí' : 'No'}
              </label>
            );
          })}
        </div>
      );
    }

    if (type === 'select') {
      return marcoControl(
        'relative',
        <>
          <select
            id={idCampo}
            value={opcionSeleccionada ? String(opcionSeleccionada.value) : ''}
            onChange={manejarCambio}
            disabled={disabled}
            aria-describedby={descripciones || undefined}
            aria-invalid={error ? true : undefined}
            className="min-h-[44px] w-full appearance-none bg-transparent px-3 outline-none disabled:cursor-not-allowed"
            style={{
              fontSize: rotulo.size,
              lineHeight: rotulo.lineHeight,
              color: tokens.colors.textPrimary,
            }}
          >
            <option value="">Seleccione una opción</option>
            {options?.map((opcion) => (
              <option key={String(opcion.value)} value={String(opcion.value)}>
                {opcion.label}
              </option>
            ))}
          </select>
          <ChevronDown
            size={tokens.iconography.sizes.sm}
            strokeWidth={1.75}
            className="pointer-events-none absolute right-3"
            style={{ color: tokens.colors.textTertiary }}
            aria-hidden="true"
          />
        </>,
      );
    }

    const tipoEntrada = type === 'number' ? 'number' : type === 'date' ? 'date' : 'text';

    return marcoControl(
      '',
      <>
        <input
          id={idCampo}
          type={tipoEntrada}
          value={valorControl}
          onChange={manejarCambio}
          disabled={disabled}
          inputMode={type === 'number' ? 'decimal' : undefined}
          step={type === 'number' ? 'any' : undefined}
          aria-describedby={descripciones || undefined}
          aria-invalid={error ? true : undefined}
          className="min-h-[44px] w-full bg-transparent px-3 outline-none disabled:cursor-not-allowed"
          style={{
            fontSize: rotulo.size,
            lineHeight: rotulo.lineHeight,
            color: tokens.colors.textPrimary,
          }}
        />
        {unit ? (
          <span
            className="whitespace-nowrap px-3"
            style={{
              fontSize: insignia.size,
              lineHeight: insignia.lineHeight,
              color: tokens.colors.textTertiary,
            }}
          >
            {unit}
          </span>
        ) : null}
      </>,
    );
  };

  return (
    <div className="flex flex-col gap-1.5">
      <label
        id={idEtiqueta}
        htmlFor={type === 'boolean' ? undefined : idCampo}
        style={{
          fontSize: rotulo.size,
          lineHeight: rotulo.lineHeight,
          fontWeight: rotulo.weight,
          color: tokens.colors.textPrimary,
        }}
      >
        {label}
      </label>

      {renderControl()}

      {masked ? (
        <p
          id={idAyuda}
          className="flex items-center gap-1.5"
          style={{
            fontSize: insignia.size,
            lineHeight: insignia.lineHeight,
            color: tokens.colors.textTertiary,
          }}
        >
          <EyeOff
            size={tokens.iconography.sizes.sm}
            strokeWidth={1.75}
            aria-hidden="true"
          />
          Dato enmascarado conforme a GDPR/HIPAA
        </p>
      ) : null}

      {error ? (
        <p
          id={idError}
          role="alert"
          className="flex items-center gap-1.5"
          style={{
            fontSize: cuerpo.size,
            lineHeight: cuerpo.lineHeight,
            fontWeight: 500,
            color: tokens.colors.danger,
          }}
        >
          <AlertCircle
            size={tokens.iconography.sizes.sm}
            strokeWidth={1.75}
            aria-hidden="true"
          />
          {error}
        </p>
      ) : null}
    </div>
  );
}

export default ClinicalField;
