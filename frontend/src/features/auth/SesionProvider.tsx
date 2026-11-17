import { useCallback, useMemo, type ReactNode } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { ErrorApi, fijarToken } from '../../lib/api'
import { cerrarSesionEnServidor, refrescarSesion } from './api'
import {
  SesionContext,
  type EstadoSesion,
  type ValorSesion,
} from './SesionContext'
import type { TokenSalida, Usuario } from './types'

const CLAVE_SESION = ['sesion'] as const

export function SesionProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()

  // Al abrir o recargar la página no hay token en memoria: se intenta recuperarlo
  // con la cookie de refresh. Si el servidor dice 401, simplemente no hay sesión.
  const restauracion = useQuery({
    queryKey: CLAVE_SESION,
    queryFn: async (): Promise<Usuario | null> => {
      try {
        const tokens = await refrescarSesion()
        fijarToken(tokens.access_token)
        return tokens.usuario
      } catch (error) {
        if (error instanceof ErrorApi && error.status === 401) return null
        throw error
      }
    },
    retry: false,
    staleTime: Infinity,
    refetchOnWindowFocus: false,
  })

  const iniciarSesion = useCallback(
    (tokens: TokenSalida) => {
      fijarToken(tokens.access_token)
      queryClient.setQueryData<Usuario | null>(CLAVE_SESION, tokens.usuario)
    },
    [queryClient],
  )

  const cerrarSesion = useCallback(async () => {
    try {
      await cerrarSesionEnServidor()
    } finally {
      // Aunque el servidor no responda, en este navegador la sesión se cierra igual.
      fijarToken(null)
      queryClient.setQueryData<Usuario | null>(CLAVE_SESION, null)
      queryClient.removeQueries({
        predicate: (q) => q.queryKey[0] !== CLAVE_SESION[0],
      })
    }
  }, [queryClient])

  const usuario = restauracion.data ?? null
  const estado: EstadoSesion = restauracion.isPending
    ? 'cargando'
    : usuario
      ? 'autenticado'
      : 'anonimo'

  const valor = useMemo<ValorSesion>(
    () => ({ estado, usuario, iniciarSesion, cerrarSesion }),
    [estado, usuario, iniciarSesion, cerrarSesion],
  )

  return (
    <SesionContext.Provider value={valor}>{children}</SesionContext.Provider>
  )
}
