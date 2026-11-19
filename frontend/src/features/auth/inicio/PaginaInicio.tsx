import { Link } from 'react-router'
import { useSesion } from '../useSesion'

export function PaginaInicio() {
  const { usuario, cerrarSesion } = useSesion()

  return (
    <main className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="text-2xl font-semibold text-slate-900">
        Hola, {usuario?.nombre_completo}
      </h1>
      <p className="mt-1 text-slate-600">Rol: {usuario?.rol}</p>
      <Link
        to="/documentos"
        className="mt-6 block text-blue-700 hover:underline"
      >
        Documentos
      </Link>
      <button
        type="button"
        onClick={() => void cerrarSesion()}
        className="mt-6 rounded-md border border-slate-300 px-4 py-2 text-slate-700 hover:bg-slate-50"
      >
        Cerrar sesión
      </button>
    </main>
  )
}
