import { NavLink, Outlet } from 'react-router'
import { useSesion } from '../features/auth/useSesion'
import { IconoDocumento, IconoInicio, IconoMapa, IconoSalir } from './Iconos'
import { Marca } from './Marca'

const NOMBRES_ROL = { funcionario: 'Funcionario', encargado: 'Encargado' }

const ENLACES = [
  { a: '/', texto: 'Inicio', icono: IconoInicio, fin: true },
  { a: '/documentos', texto: 'Documentos', icono: IconoDocumento, fin: false },
  {
    a: '/ddrr-catastro',
    texto: 'DDRR y Catastro',
    icono: IconoMapa,
    fin: false,
  },
]

function iniciales(nombre: string): string {
  return nombre
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((parte) => parte[0]?.toUpperCase())
    .join('')
}

export function DisenoApp() {
  const { usuario, cerrarSesion } = useSesion()

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/85 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-6xl items-center gap-6 px-4 sm:px-6">
          <Marca />

          <nav className="ml-2 hidden items-center gap-1 sm:flex">
            {ENLACES.map(({ a, texto, icono: Icono, fin }) => (
              <NavLink
                key={a}
                to={a}
                end={fin}
                className={({ isActive }) =>
                  `flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-marca-50 text-marca-800'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                  }`
                }
              >
                <Icono className="size-4" />
                {texto}
              </NavLink>
            ))}
          </nav>

          <div className="ml-auto flex items-center gap-3">
            {usuario && (
              <div className="hidden items-center gap-3 md:flex">
                <div className="text-right leading-tight">
                  <p className="text-sm font-medium text-slate-900">
                    {usuario.nombre_completo}
                  </p>
                  <p className="text-xs text-slate-500">
                    {NOMBRES_ROL[usuario.rol]}
                  </p>
                </div>
                <div className="flex size-9 items-center justify-center rounded-full bg-marca-100 text-xs font-semibold text-marca-800 ring-1 ring-marca-200">
                  {iniciales(usuario.nombre_completo)}
                </div>
              </div>
            )}
            <button
              type="button"
              onClick={() => void cerrarSesion()}
              title="Cerrar sesión"
              className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900"
            >
              <IconoSalir className="size-4" />
              <span className="hidden sm:inline">Salir</span>
            </button>
          </div>
        </div>

        {/* Navegación en pantallas pequeñas. */}
        <nav className="flex gap-1 border-t border-slate-100 px-4 py-2 sm:hidden">
          {ENLACES.map(({ a, texto, icono: Icono, fin }) => (
            <NavLink
              key={a}
              to={a}
              end={fin}
              className={({ isActive }) =>
                `flex flex-1 items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-medium ${
                  isActive ? 'bg-marca-50 text-marca-800' : 'text-slate-600'
                }`
              }
            >
              <Icono className="size-4" />
              {texto}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10">
        <Outlet />
      </main>
    </div>
  )
}
