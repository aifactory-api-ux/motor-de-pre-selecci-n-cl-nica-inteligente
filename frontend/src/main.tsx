/**
 * Punto de entrada de la aplicación React.
 *
 * Monta el componente raíz sobre el contenedor `#root` declarado en
 * `frontend/public/index.html` y carga las hojas de estilo globales: primero
 * las directivas de Tailwind y la capa base del sistema de diseño, y después
 * los estilos globales de la aplicación.
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import App from './App';
import './styles/tailwind.css';
import './index.css';

const contenedor = document.getElementById('root');

if (!contenedor) {
  throw new Error(
    'No se encontró el contenedor raíz "#root" en frontend/public/index.html.',
  );
}

createRoot(contenedor).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
