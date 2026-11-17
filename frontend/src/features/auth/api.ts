import { api } from '../../lib/api'
import type { LoginSalida, TokenSalida } from './types'

export function iniciarLogin(
  username: string,
  password: string,
): Promise<LoginSalida> {
  return api<LoginSalida>('/auth/login', {
    metodo: 'POST',
    cuerpo: { username, password },
  })
}

// El refresh token viaja solo, en la cookie httpOnly: no se le pasa nada.
export function refrescarSesion(): Promise<TokenSalida> {
  return api<TokenSalida>('/auth/refresh', { metodo: 'POST' })
}

export function cerrarSesionEnServidor(): Promise<void> {
  return api<void>('/auth/logout', { metodo: 'POST' })
}
