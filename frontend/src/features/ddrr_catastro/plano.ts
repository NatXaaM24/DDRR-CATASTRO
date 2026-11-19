// Convierte un anillo en lon/lat (SRID 4326) en puntos de un SVG.
// A escala de un predio basta una proyección equirectangular local:
// la longitud se corrige por el coseno de la latitud para no deformar.

export interface Plano {
  puntos: string
  ancho: number
  alto: number
}

export function anilloASvg(
  anillo: [number, number][],
  lado = 200,
  margen = 16,
): Plano {
  const latMedia =
    anillo.reduce((suma, [, lat]) => suma + lat, 0) / anillo.length
  const factor = Math.cos((latMedia * Math.PI) / 180)
  const xy = anillo.map(([lon, lat]) => [lon * factor, -lat] as const)

  const xs = xy.map(([x]) => x)
  const ys = xy.map(([, y]) => y)
  const minX = Math.min(...xs)
  const minY = Math.min(...ys)
  const extension = Math.max(Math.max(...xs) - minX, Math.max(...ys) - minY)
  const escala = extension > 0 ? (lado - 2 * margen) / extension : 1

  const puntos = xy
    .map(
      ([x, y]) =>
        `${(margen + (x - minX) * escala).toFixed(2)},${(margen + (y - minY) * escala).toFixed(2)}`,
    )
    .join(' ')

  return {
    puntos,
    ancho: (Math.max(...xs) - minX) * escala + 2 * margen,
    alto: (Math.max(...ys) - minY) * escala + 2 * margen,
  }
}
