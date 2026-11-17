import type {
  startAuthentication,
  startRegistration,
} from '@simplewebauthn/browser'
import { api } from '../../lib/api'
import type { LoginSalida, TokenSalida } from './types'

// Los tipos se deducen de la propia librería (así no dependen de nombres internos).
type OpcionesRegistro = Parameters<typeof startRegistration>[0]['optionsJSON']
type OpcionesAutenticacion = Parameters<
  typeof startAuthentication
>[0]['optionsJSON']
type RespuestaRegistro = Awaited<ReturnType<typeof startRegistration>>
type RespuestaAutenticacion = Awaited<ReturnType<typeof startAuthentication>>

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

// ---------- Paso 2: biometría (todas llevan el preauth_token) ----------

export function pedirOpcionesRegistro(
  preauthToken: string,
): Promise<OpcionesRegistro> {
  return api<OpcionesRegistro>('/auth/webauthn/registro/opciones', {
    metodo: 'POST',
    token: preauthToken,
  })
}

export function verificarRegistro(
  preauthToken: string,
  credencial: RespuestaRegistro,
  nombre: string,
): Promise<TokenSalida> {
  return api<TokenSalida>('/auth/webauthn/registro/verificar', {
    metodo: 'POST',
    token: preauthToken,
    cuerpo: { credencial, nombre },
  })
}

export function pedirOpcionesAutenticacion(
  preauthToken: string,
): Promise<OpcionesAutenticacion> {
  return api<OpcionesAutenticacion>('/auth/webauthn/autenticacion/opciones', {
    metodo: 'POST',
    token: preauthToken,
  })
}

export function verificarAutenticacion(
  preauthToken: string,
  credencial: RespuestaAutenticacion,
): Promise<TokenSalida> {
  return api<TokenSalida>('/auth/webauthn/autenticacion/verificar', {
    metodo: 'POST',
    token: preauthToken,
    cuerpo: { credencial },
  })
}
