import { describe, expect, it } from 'vitest'
import { anilloASvg } from './plano'

describe('anilloASvg', () => {
  const cuadrado: [number, number][] = [
    [-66.1, -17.4],
    [-66.099, -17.4],
    [-66.099, -17.399],
    [-66.1, -17.399],
    [-66.1, -17.4],
  ]

  it('ajusta el polígono dentro del lienzo con su margen', () => {
    const { puntos, ancho, alto } = anilloASvg(cuadrado, 200, 16)
    const coordenadas = puntos
      .split(' ')
      .flatMap((par) => par.split(',').map(Number))
    expect(Math.min(...coordenadas)).toBeCloseTo(16)
    expect(Math.max(...coordenadas)).toBeCloseTo(184)
    expect(Math.max(ancho, alto)).toBeCloseTo(200)
  })

  it('corrige la longitud por la latitud (no deforma el predio)', () => {
    const { ancho, alto } = anilloASvg(cuadrado, 200, 0)
    // Un grado de longitud mide menos que uno de latitud a 17° S.
    expect(ancho / alto).toBeCloseTo(Math.cos((17.3995 * Math.PI) / 180), 3)
  })

  it('el norte queda arriba', () => {
    const { puntos } = anilloASvg(cuadrado, 200, 0)
    const [, ySur] = puntos.split(' ')[0].split(',').map(Number)
    const [, yNorte] = puntos.split(' ')[2].split(',').map(Number)
    expect(yNorte).toBeLessThan(ySur)
  })
})
