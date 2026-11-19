import { useQuery } from '@tanstack/react-query'
import {
  useState,
  type ComponentType,
  type ReactNode,
  type SVGProps,
} from 'react'
import { IconoBuscar, IconoLibro, IconoMapa } from '../../components/Iconos'
import {
  Aviso,
  Boton,
  EncabezadoPagina,
  EstadoVacio,
  Girador,
  Tarjeta,
} from '../../components/ui'
import { ErrorApi } from '../../lib/api'
import { obtenerPartida, obtenerPredio } from './api'
import { FormularioBusqueda } from './FormularioBusqueda'
import { PlanoPredio } from './PlanoPredio'

const numero = new Intl.NumberFormat('es-BO', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})
const fecha = new Intl.DateTimeFormat('es-BO', { dateStyle: 'long' })

function superficie(m2: string): string {
  return `${numero.format(Number(m2))} m²`
}

function Dato({
  etiqueta,
  children,
  mono = false,
}: {
  etiqueta: string
  children: ReactNode
  mono?: boolean
}) {
  return (
    <div>
      <dt className="text-xs font-medium tracking-wide text-slate-500 uppercase">
        {etiqueta}
      </dt>
      <dd className={`mt-1 text-sm text-slate-900 ${mono ? 'font-mono' : ''}`}>
        {children}
      </dd>
    </div>
  )
}

function CabeceraPanel({
  icono: Icono,
  titulo,
  subtitulo,
}: {
  icono: ComponentType<SVGProps<SVGSVGElement>>
  titulo: string
  subtitulo: string
}) {
  return (
    <div className="flex items-center gap-3">
      <span className="flex size-10 items-center justify-center rounded-xl bg-marca-50 text-marca-700 ring-1 ring-marca-100">
        <Icono className="size-5" />
      </span>
      <div>
        <h2 className="text-base font-semibold text-slate-900">{titulo}</h2>
        <p className="text-xs text-slate-500">{subtitulo}</p>
      </div>
    </div>
  )
}

// Estado común de una búsqueda: vacía, cargando, no encontrada o con error.
function EstadoBusqueda({
  consultado,
  cargando,
  error,
  vacio,
}: {
  consultado: string
  cargando: boolean
  error: Error | null
  vacio: string
}) {
  if (!consultado) return <EstadoVacio icono={IconoBuscar} titulo={vacio} />
  if (cargando)
    return (
      <div
        role="status"
        className="flex items-center justify-center gap-2.5 py-14 text-sm text-slate-500"
      >
        <Girador className="size-4 text-marca-600" />
        Consultando…
      </div>
    )
  if (error instanceof ErrorApi && error.status === 404)
    return (
      <EstadoVacio
        icono={IconoBuscar}
        titulo="Sin resultados"
        descripcion={`No hay ningún registro con el identificador «${consultado}».`}
      />
    )
  if (error)
    return (
      <Aviso tipo="error">
        {error instanceof ErrorApi
          ? error.message
          : 'No se pudo completar la consulta.'}
      </Aviso>
    )
  return null
}

export function PaginaConsultas() {
  const [matricula, setMatricula] = useState('')
  const [codigo, setCodigo] = useState('')

  const partida = useQuery({
    queryKey: ['ddrr', 'partida', matricula],
    queryFn: () => obtenerPartida(matricula),
    enabled: matricula !== '',
  })

  const predio = useQuery({
    queryKey: ['catastro', 'predio', codigo],
    queryFn: () => obtenerPredio(codigo),
    enabled: codigo !== '',
  })

  return (
    <>
      <EncabezadoPagina
        titulo="DDRR y Catastro"
        descripcion="Consulta una partida de Derechos Reales o un predio de Catastro por su identificador."
      />

      <div className="grid items-start gap-6 lg:grid-cols-2">
        {/* Derechos Reales. */}
        <Tarjeta className="p-6">
          <CabeceraPanel
            icono={IconoLibro}
            titulo="Derechos Reales"
            subtitulo="Partida por matrícula del folio real"
          />
          <div className="mt-5">
            <FormularioBusqueda
              id="matricula"
              etiqueta="Matrícula"
              ejemplo="3.01.1.01.0000001"
              valorInicial={matricula}
              buscando={partida.isFetching}
              onBuscar={setMatricula}
            />
          </div>

          <div className="mt-6">
            <EstadoBusqueda
              consultado={matricula}
              cargando={partida.isPending && partida.isFetching}
              error={partida.error}
              vacio="Escribe una matrícula para consultar"
            />
            {partida.data && (
              <div className="rounded-xl bg-slate-50/70 p-5 ring-1 ring-slate-200">
                <dl className="grid gap-5 sm:grid-cols-2">
                  <div className="sm:col-span-2">
                    <Dato etiqueta="Matrícula" mono>
                      {partida.data.matricula}
                    </Dato>
                  </div>
                  <Dato etiqueta="Titular">{partida.data.titular_nombre}</Dato>
                  <Dato etiqueta="CI del titular" mono>
                    {partida.data.titular_ci}
                  </Dato>
                  <Dato etiqueta="Superficie">
                    {superficie(partida.data.superficie_m2)}
                  </Dato>
                  <Dato etiqueta="Inscripción">
                    {fecha.format(
                      new Date(`${partida.data.fecha_inscripcion}T00:00:00`),
                    )}
                  </Dato>
                  <div className="sm:col-span-2">
                    <Dato etiqueta="Dirección">{partida.data.direccion}</Dato>
                  </div>
                  <div className="sm:col-span-2">
                    <Dato etiqueta="Código catastral" mono>
                      {partida.data.codigo_catastral}
                    </Dato>
                  </div>
                </dl>
                <Boton
                  variante="secundario"
                  ancho
                  className="mt-5"
                  onClick={() => setCodigo(partida.data.codigo_catastral)}
                >
                  <IconoMapa className="size-4" />
                  Consultar este predio en Catastro
                </Boton>
              </div>
            )}
          </div>
        </Tarjeta>

        {/* Catastro. */}
        <Tarjeta className="p-6">
          <CabeceraPanel
            icono={IconoMapa}
            titulo="Catastro"
            subtitulo="Predio por código catastral"
          />
          <div className="mt-5">
            {/* La clave reinicia el formulario cuando el código llega desde la partida. */}
            <FormularioBusqueda
              key={codigo}
              id="codigo"
              etiqueta="Código catastral"
              ejemplo="01-010-001-0001"
              valorInicial={codigo}
              buscando={predio.isFetching}
              onBuscar={setCodigo}
            />
          </div>

          <div className="mt-6">
            <EstadoBusqueda
              consultado={codigo}
              cargando={predio.isPending && predio.isFetching}
              error={predio.error}
              vacio="Escribe un código catastral para consultar"
            />
            {predio.data && (
              <div className="space-y-5 rounded-xl bg-slate-50/70 p-5 ring-1 ring-slate-200">
                <dl className="grid gap-5 sm:grid-cols-2">
                  <div className="sm:col-span-2">
                    <Dato etiqueta="Código catastral" mono>
                      {predio.data.codigo_catastral}
                    </Dato>
                  </div>
                  <Dato etiqueta="Propietario">
                    {predio.data.propietario_nombre}
                  </Dato>
                  <Dato etiqueta="CI del propietario" mono>
                    {predio.data.propietario_ci}
                  </Dato>
                  <Dato etiqueta="Superficie">
                    {superficie(predio.data.superficie_m2)}
                  </Dato>
                  <Dato etiqueta="Distrito">{predio.data.distrito}</Dato>
                  <div className="sm:col-span-2">
                    <Dato etiqueta="Dirección">{predio.data.direccion}</Dato>
                  </div>
                </dl>
                <PlanoPredio geometria={predio.data.geometria} />
              </div>
            )}
          </div>
        </Tarjeta>
      </div>
    </>
  )
}
