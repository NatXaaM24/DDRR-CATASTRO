// Cliente único para la API /api/v1 (R-FRT-2).
// El token de acceso vive SOLO en esta variable de memoria (R-SEG-5):
// nunca en localStorage ni sessionStorage.

export class ErrorApi extends Error {
  readonly status: number
  readonly code: string

  constructor(status: number, code: string, message: string) {
    super(message)
    this.name = 'ErrorApi'
    this.status = status
    this.code = code
  }
}

let tokenDeAcceso: string | null = null

export function fijarToken(token: string | null): void {
  tokenDeAcceso = token
}

const BASE = '/api/v1'

interface Opciones {
  metodo?: 'GET' | 'POST' | 'PATCH' | 'DELETE'
  cuerpo?: unknown
  // Para pasos sin sesión completa (p. ej. el preauth_token del login).
  token?: string | null
}

interface CuerpoDeError {
  code?: string
  message?: string
}

export async function api<T>(
  ruta: string,
  opciones: Opciones = {},
): Promise<T> {
  const { metodo = 'GET', cuerpo, token = tokenDeAcceso } = opciones

  const cabeceras: Record<string, string> = {}
  if (cuerpo !== undefined) cabeceras['Content-Type'] = 'application/json'
  if (token) cabeceras.Authorization = `Bearer ${token}`

  let respuesta: Response
  try {
    respuesta = await fetch(`${BASE}${ruta}`, {
      method: metodo,
      headers: cabeceras,
      body: cuerpo !== undefined ? JSON.stringify(cuerpo) : undefined,
    })
  } catch {
    throw new ErrorApi(
      0,
      'sin_conexion',
      'No se pudo conectar con el servidor.',
    )
  }

  if (!respuesta.ok) {
    let code = 'error_desconocido'
    let message = 'Ocurrió un error inesperado.'
    try {
      const datos = (await respuesta.json()) as CuerpoDeError
      code = datos.code ?? code
      message = datos.message ?? message
    } catch {
      // La respuesta no era JSON: se queda el mensaje genérico.
    }
    throw new ErrorApi(respuesta.status, code, message)
  }

  if (respuesta.status === 204) return undefined as T
  return (await respuesta.json()) as T
}
