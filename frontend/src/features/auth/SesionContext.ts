import { createContext } from 'react'
import type { TokenSalida, Usuario } from './types'

export type EstadoSesion = 'cargando' | 'anonimo' | 'autenticado'

export interface ValorSesion {
  estado: EstadoSesion
  usuario: Usuario | null
  iniciarSesion: (tokens: TokenSalida) => void
  cerrarSesion: () => Promise<void>
}

export const SesionContext = createContext<ValorSesion | null>(null)
