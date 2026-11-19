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

// La sesión registra aquí cómo conseguir un token nuevo (con la cookie de refresh).
// Devuelve el token nuevo, o null si la sesión ya no se puede recuperar.
type Renovador = () => Promise<string | null>

let renovador: Renovador | null = null
let renovacionEnCurso: Promise<string | null> | null = null

export function configurarRenovacion(funcion: Renovador | null): void {
  renovador = funcion
}

function renovarToken(): Promise<string | null> {
  if (renovador === null) return Promise.resolve(null)
  // Si ya hay una renovación en marcha, todas las peticiones esperan la misma.
  renovacionEnCurso ??= renovador().finally(() => {
    renovacionEnCurso = null
  })
  return renovacionEnCurso
}

const BASE = '/api/v1'

interface Opciones {
  metodo?: 'GET' | 'POST' | 'PATCH' | 'DELETE'
  cuerpo?: unknown
  // Para pasos sin sesión completa (p. ej. el preauth_token del login).
  token?: string | null
  // false en login, refresh y logout: ahí un 401 no se arregla renovando.
  renovar?: boolean
  // 'blob' para respuestas binarias (p. ej. el PDF de un documento).
  formato?: 'json' | 'blob'
}

interface CuerpoDeError {
  code?: string
  message?: string
}

async function peticion<T>(
  ruta: string,
  opciones: Opciones,
  token: string | null,
): Promise<T> {
  const { metodo = 'GET', cuerpo } = opciones

  // Un FormData (subida de archivos) se envía tal cual: el navegador fija
  // el Content-Type multipart con su boundary.
  const esFormulario = cuerpo instanceof FormData
  const cabeceras: Record<string, string> = {}
  if (cuerpo !== undefined && !esFormulario)
    cabeceras['Content-Type'] = 'application/json'
  if (token) cabeceras.Authorization = `Bearer ${token}`

  let respuesta: Response
  try {
    respuesta = await fetch(`${BASE}${ruta}`, {
      method: metodo,
      headers: cabeceras,
      body: esFormulario
        ? cuerpo
        : cuerpo !== undefined
          ? JSON.stringify(cuerpo)
          : undefined,
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
  if (opciones.formato === 'blob') return (await respuesta.blob()) as T
  return (await respuesta.json()) as T
}

export async function api<T>(
  ruta: string,
  opciones: Opciones = {},
): Promise<T> {
  const { renovar = true, token } = opciones
  try {
    return await peticion<T>(
      ruta,
      opciones,
      token !== undefined ? token : tokenDeAcceso,
    )
  } catch (error) {
    const sePuedeRenovar =
      renovar &&
      token === undefined &&
      error instanceof ErrorApi &&
      error.status === 401
    if (!sePuedeRenovar) throw error

    const nuevoToken = await renovarToken()
    if (nuevoToken === null) throw error
    return peticion<T>(ruta, opciones, nuevoToken)
  }
}
