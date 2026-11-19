import { Link } from 'react-router'
import { Emblema } from './Marca'
import { IconoCandado } from './Iconos'
import { Girador } from './ui'
import { clasesBoton } from './estilos'

export function PantallaDeCarga() {
  return (
    <main
      role="status"
      className="flex min-h-screen flex-col items-center justify-center gap-5"
    >
      <Emblema className="size-12" />
      <div className="flex items-center gap-2.5 text-sm text-slate-500">
        <Girador className="size-4 text-marca-600" />
        Cargando…
      </div>
    </main>
  )
}

export function SinPermiso() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-4 text-center">
      <div className="flex size-14 items-center justify-center rounded-2xl bg-white text-marca-700 shadow-xs ring-1 ring-slate-200">
        <IconoCandado className="size-7" />
      </div>
      <h1 className="mt-5 text-xl font-semibold tracking-tight text-slate-900">
        Sin permiso
      </h1>
      <p className="mt-1.5 text-sm text-slate-500">
        Tu rol no tiene acceso a esta página.
      </p>
      <Link to="/" className={`${clasesBoton('secundario')} mt-6`}>
        Volver al inicio
      </Link>
    </main>
  )
}
