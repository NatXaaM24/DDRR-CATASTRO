import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ErrorApi, api, configurarRenovacion, fijarToken } from './api'

function responder(estado: number, cuerpo?: unknown): Response {
  return new Response(cuerpo === undefined ? null : JSON.stringify(cuerpo), {
    status: estado,
  })
}

function cabecera(
  llamada: Parameters<typeof fetch>,
  nombre: string,
): string | undefined {
  const cabeceras = llamada[1]?.headers as Record<string, string> | undefined
  return cabeceras?.[nombre]
}

const fetchFalso = vi.fn<typeof fetch>()

beforeEach(() => {
  fetchFalso.mockReset()
  vi.stubGlobal('fetch', fetchFalso)
  fijarToken(null)
  configurarRenovacion(null)
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('api', () => {
  it('adjunta el token de acceso', async () => {
    fijarToken('abc')
    fetchFalso.mockResolvedValueOnce(responder(200, { ok: true }))
    await api('/algo')
    expect(cabecera(fetchFalso.mock.calls[0], 'Authorization')).toBe(
      'Bearer abc',
    )
  })

  it('convierte el error {code, message} del servidor en ErrorApi', async () => {
    fetchFalso.mockResolvedValueOnce(
      responder(429, {
        code: 'demasiados_intentos',
        message: 'Demasiados intentos.',
      }),
    )
    const promesa = api('/auth/login', { renovar: false })
    await expect(promesa).rejects.toBeInstanceOf(ErrorApi)
    await expect(promesa).rejects.toMatchObject({
      status: 429,
      code: 'demasiados_intentos',
      message: 'Demasiados intentos.',
    })
  })

  it('devuelve undefined cuando la respuesta es 204', async () => {
    fetchFalso.mockResolvedValueOnce(responder(204))
    await expect(
      api('/auth/logout', { metodo: 'POST' }),
    ).resolves.toBeUndefined()
  })

  it('avisa con sin_conexion cuando no hay red', async () => {
    fetchFalso.mockRejectedValueOnce(new TypeError('fallo de red'))
    await expect(api('/algo')).rejects.toMatchObject({
      status: 0,
      code: 'sin_conexion',
    })
  })
})

describe('renovación del token', () => {
  const noAutenticado = { code: 'no_autenticado', message: 'Sesión expirada.' }

  it('ante un 401 renueva el token y repite la petición una vez', async () => {
    const renovar = vi.fn().mockResolvedValue('nuevo')
    configurarRenovacion(renovar)
    fijarToken('viejo')
    fetchFalso
      .mockResolvedValueOnce(responder(401, noAutenticado))
      .mockResolvedValueOnce(responder(200, { dato: 1 }))

    await expect(api('/algo')).resolves.toEqual({ dato: 1 })
    expect(renovar).toHaveBeenCalledTimes(1)
    expect(cabecera(fetchFalso.mock.calls[1], 'Authorization')).toBe(
      'Bearer nuevo',
    )
  })

  it('si no se puede renovar, deja pasar el error original', async () => {
    configurarRenovacion(vi.fn().mockResolvedValue(null))
    fetchFalso.mockResolvedValueOnce(responder(401, noAutenticado))
    await expect(api('/algo')).rejects.toMatchObject({ status: 401 })
    expect(fetchFalso).toHaveBeenCalledTimes(1)
  })

  it('varias peticiones fallidas a la vez renuevan una sola vez', async () => {
    const renovar = vi.fn().mockResolvedValue('nuevo')
    configurarRenovacion(renovar)
    fijarToken('viejo')
    fetchFalso.mockImplementation((_url, init) => {
      const cabeceras = init?.headers as Record<string, string>
      return Promise.resolve(
        cabeceras.Authorization === 'Bearer nuevo'
          ? responder(200, {})
          : responder(401, noAutenticado),
      )
    })

    await Promise.all([api('/a'), api('/b')])
    expect(renovar).toHaveBeenCalledTimes(1)
  })

  it('no renueva con token propio (preauth) ni con renovar: false', async () => {
    const renovar = vi.fn().mockResolvedValue('nuevo')
    configurarRenovacion(renovar)
    fetchFalso.mockImplementation(() =>
      Promise.resolve(responder(401, noAutenticado)),
    )

    await expect(api('/x', { token: 'preauth' })).rejects.toMatchObject({
      status: 401,
    })
    await expect(api('/y', { renovar: false })).rejects.toMatchObject({
      status: 401,
    })
    expect(renovar).not.toHaveBeenCalled()
  })

  it('envía un FormData sin convertirlo a JSON ni fijar Content-Type', async () => {
    const formulario = new FormData()
    formulario.append('tipo', 'otro')
    fetchFalso.mockResolvedValueOnce(responder(201, { ok: true }))
    await api('/documentos', { metodo: 'POST', cuerpo: formulario })
    const llamada = fetchFalso.mock.calls[0]
    expect(llamada[1]?.body).toBe(formulario)
    expect(cabecera(llamada, 'Content-Type')).toBeUndefined()
  })
})
