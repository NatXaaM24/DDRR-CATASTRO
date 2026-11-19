import { api } from '../../lib/api'
import type { Partida, Predio } from './types'

export function obtenerPartida(matricula: string): Promise<Partida> {
  return api<Partida>(
    `/ddrr-catastro/partidas/${encodeURIComponent(matricula)}`,
  )
}

export function obtenerPredio(codigo: string): Promise<Predio> {
  return api<Predio>(`/ddrr-catastro/predios/${encodeURIComponent(codigo)}`)
}
