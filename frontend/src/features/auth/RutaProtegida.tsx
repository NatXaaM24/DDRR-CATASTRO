import { Navigate, Outlet } from 'react-router'
import { PantallaDeCarga, SinPermiso } from '../../components/Estados'
import type { Rol } from './types'
import { useSesion } from './useSesion'

interface Props {
  roles?: Rol[]
}

export function RutaProtegida({ roles }: Props) {
  const { estado, usuario } = useSesion()

  // Mientras se intenta recuperar la sesión no se decide nada (evita el parpadeo del login).
  if (estado === 'cargando') return <PantallaDeCarga />
  if (!usuario) return <Navigate to="/login" replace />
  if (roles && !roles.includes(usuario.rol)) return <SinPermiso />

  return <Outlet />
}
