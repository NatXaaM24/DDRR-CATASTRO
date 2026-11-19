import { anilloASvg } from './plano'
import type { PoligonoGeoJson } from './types'

const LADO = 220

export function PlanoPredio({ geometria }: { geometria: PoligonoGeoJson }) {
  const { puntos, ancho, alto } = anilloASvg(geometria.coordinates[0], LADO)

  return (
    <figure className="overflow-hidden rounded-xl bg-slate-50 ring-1 ring-slate-200">
      <svg
        viewBox={`0 0 ${LADO} ${LADO}`}
        className="mx-auto block aspect-square w-full max-w-64"
        role="img"
        aria-label="Plano del predio"
      >
        <defs>
          <pattern
            id="cuadricula-plano"
            width="20"
            height="20"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M20 0H0v20"
              fill="none"
              className="stroke-slate-200"
              strokeWidth="1"
            />
          </pattern>
        </defs>
        <rect width={LADO} height={LADO} fill="url(#cuadricula-plano)" />
        {/* Centra el polígono en el lienzo. */}
        <g transform={`translate(${(LADO - ancho) / 2} ${(LADO - alto) / 2})`}>
          <polygon
            points={puntos}
            className="fill-marca-500/15 stroke-marca-700"
            strokeWidth="2"
            strokeLinejoin="round"
          />
        </g>
        {/* Indicador de norte. */}
        <g transform="translate(198 26)" className="fill-slate-500">
          <path d="M0 -12 5 4 0 1 -5 4z" />
          <text
            y="16"
            textAnchor="middle"
            className="fill-slate-500 text-[9px] font-semibold"
          >
            N
          </text>
        </g>
      </svg>
      <figcaption className="border-t border-slate-200 px-4 py-2 text-xs text-slate-500">
        Polígono registrado en Catastro (WGS 84)
      </figcaption>
    </figure>
  )
}
