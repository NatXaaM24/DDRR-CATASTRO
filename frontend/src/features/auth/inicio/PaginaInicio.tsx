import type { ComponentType, SVGProps } from 'react'
import { Link } from 'react-router'
import {
  IconoDerecha,
  IconoDocumento,
  IconoMapa,
  IconoSubir,
} from '../../../components/Iconos'
import { Insignia } from '../../../components/ui'
import { useSesion } from '../useSesion'

interface Acceso {
  a: string
  titulo: string
  texto: string
  icono: ComponentType<SVGProps<SVGSVGElement>>
}

function saludo(): string {
  const hora = new Date().getHours()
  if (hora < 12) return 'Buenos días'
  if (hora < 19) return 'Buenas tardes'
  return 'Buenas noches'
}

export function PaginaInicio() {
  const { usuario } = useSesion()
  const esFuncionario = usuario?.rol === 'funcionario'

  const accesos: Acceso[] = [
    {
      a: '/documentos',
      titulo: 'Documentos',
      texto: esFuncionario
        ? 'Consulta los documentos que subiste y ábrelos en el visor.'
        : 'Consulta todos los documentos subidos por el personal.',
      icono: IconoDocumento,
    },
  ]
  accesos.push({
    a: '/ddrr-catastro',
    titulo: 'DDRR y Catastro',
    texto: 'Consulta partidas de Derechos Reales y predios de Catastro.',
    icono: IconoMapa,
  })
  if (esFuncionario) {
    accesos.push({
      a: '/documentos',
      titulo: 'Subir documento',
      texto: 'Agrega un PDF para su revisión. Se valida su tipo y tamaño.',
      icono: IconoSubir,
    })
  }

  return (
    <>
      <div className="mb-10">
        <p className="text-sm font-medium text-marca-700">{saludo()}</p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-900">
          {usuario?.nombre_completo}
        </h1>
        <div className="mt-3 flex items-center gap-2 text-sm text-slate-500">
          <Insignia tono="marca">
            {esFuncionario ? 'Funcionario' : 'Encargado'}
          </Insignia>
          <span>@{usuario?.username}</span>
        </div>
      </div>

      <h2 className="mb-4 text-sm font-semibold tracking-wide text-slate-500 uppercase">
        Accesos
      </h2>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {accesos.map(({ a, titulo, texto, icono: Icono }) => (
          <Link
            key={titulo}
            to={a}
            className="group relative flex flex-col rounded-2xl bg-white p-6 shadow-xs ring-1 ring-slate-200/80 transition hover:-translate-y-0.5 hover:shadow-md hover:ring-marca-200 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-marca-700"
          >
            <span className="flex size-11 items-center justify-center rounded-xl bg-marca-50 text-marca-700 ring-1 ring-marca-100 transition group-hover:bg-marca-700 group-hover:text-white">
              <Icono className="size-5" />
            </span>
            <span className="mt-5 text-base font-semibold text-slate-900">
              {titulo}
            </span>
            <span className="mt-1 text-sm leading-relaxed text-slate-500">
              {texto}
            </span>
            <IconoDerecha className="absolute top-6 right-6 size-5 text-slate-300 transition group-hover:translate-x-0.5 group-hover:text-marca-600" />
          </Link>
        ))}
      </div>
    </>
  )
}
