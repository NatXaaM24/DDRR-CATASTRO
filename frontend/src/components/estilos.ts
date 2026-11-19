// Clases de Tailwind compartidas (en su propio archivo por Fast Refresh).

export type Variante = 'primario' | 'secundario' | 'fantasma'

const VARIANTES: Record<Variante, string> = {
  primario:
    'bg-marca-700 text-white shadow-sm hover:bg-marca-800 focus-visible:outline-marca-700',
  secundario:
    'bg-white text-slate-700 ring-1 ring-slate-300 ring-inset shadow-xs hover:bg-slate-50 focus-visible:outline-marca-700',
  fantasma:
    'text-slate-600 hover:bg-slate-100 hover:text-slate-900 focus-visible:outline-marca-700',
}

export function clasesBoton(variante: Variante = 'primario', ancho = false) {
  return `inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 disabled:pointer-events-none disabled:opacity-55 ${VARIANTES[variante]} ${ancho ? 'w-full' : ''}`
}

export const clasesCampo =
  'block w-full rounded-lg border-0 bg-white px-3.5 py-2.5 text-sm text-slate-900 shadow-xs ring-1 ring-slate-300 ring-inset placeholder:text-slate-400 transition focus:ring-2 focus:ring-marca-600 focus:outline-none aria-[invalid=true]:ring-red-400'
