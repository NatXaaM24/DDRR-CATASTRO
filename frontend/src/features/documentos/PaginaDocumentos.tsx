import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { useNavigate } from 'react-router'
import {
  IconoBandeja,
  IconoDerecha,
  IconoDocumento,
  IconoIzquierda,
} from '../../components/Iconos'
import {
  Aviso,
  Boton,
  EncabezadoPagina,
  EstadoVacio,
  Girador,
  Tarjeta,
} from '../../components/ui'
import { ErrorApi } from '../../lib/api'
import { useSesion } from '../auth/useSesion'
import { TAMANO_PAGINA, listarDocumentos } from './api'
import { FormularioSubida } from './FormularioSubida'
import { formatearFecha, formatearTamano } from './formato'
import { InsigniaEstado } from './InsigniaEstado'
import { NOMBRES_TIPO } from './types'

export function PaginaDocumentos() {
  const { usuario } = useSesion()
  const navegar = useNavigate()
  const [pagina, setPagina] = useState(1)
  const esFuncionario = usuario?.rol === 'funcionario'

  const consulta = useQuery({
    queryKey: ['documentos', pagina],
    queryFn: () => listarDocumentos(pagina),
    placeholderData: keepPreviousData,
  })

  const total = consulta.data?.total ?? 0
  const totalPaginas = Math.max(1, Math.ceil(total / TAMANO_PAGINA))
  const desde = total === 0 ? 0 : (pagina - 1) * TAMANO_PAGINA + 1
  const hasta = Math.min(pagina * TAMANO_PAGINA, total)

  const lista = (
    <Tarjeta className="overflow-hidden">
      <div className="flex items-center justify-between border-b border-slate-200/80 px-6 py-4">
        <h2 className="text-base font-semibold text-slate-900">
          {esFuncionario ? 'Mis documentos' : 'Todos los documentos'}
        </h2>
        {consulta.isFetching && <Girador className="size-4 text-marca-600" />}
      </div>

      {consulta.isPending && (
        <div
          role="status"
          className="flex items-center justify-center gap-2.5 py-16 text-sm text-slate-500"
        >
          <Girador className="size-4 text-marca-600" />
          Cargando documentos…
        </div>
      )}

      {consulta.isError && (
        <div className="p-6">
          <Aviso tipo="error">
            {consulta.error instanceof ErrorApi
              ? consulta.error.message
              : 'No se pudieron cargar los documentos.'}
          </Aviso>
        </div>
      )}

      {consulta.data && consulta.data.items.length === 0 && (
        <EstadoVacio
          icono={IconoBandeja}
          titulo="Todavía no hay documentos"
          descripcion={
            esFuncionario
              ? 'Sube tu primer PDF con el formulario para empezar.'
              : 'Aquí aparecerán los documentos que suba el personal.'
          }
        />
      )}

      {consulta.data && consulta.data.items.length > 0 && (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50/80 text-xs font-medium tracking-wide text-slate-500 uppercase">
                <tr>
                  <th className="px-6 py-3 font-medium">Documento</th>
                  <th className="px-3 py-3 font-medium">Estado</th>
                  <th className="hidden px-3 py-3 font-medium md:table-cell">
                    Tamaño
                  </th>
                  <th className="px-6 py-3 text-right font-medium">Subido</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {consulta.data.items.map((documento) => (
                  <tr
                    key={documento.id}
                    tabIndex={0}
                    onClick={() => void navegar(`/documentos/${documento.id}`)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter')
                        void navegar(`/documentos/${documento.id}`)
                    }}
                    className="group cursor-pointer transition-colors hover:bg-marca-50/40 focus-visible:bg-marca-50/60 focus-visible:outline-none"
                  >
                    <td className="px-6 py-3.5">
                      <div className="flex items-center gap-3">
                        <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-slate-500 transition group-hover:bg-white group-hover:text-marca-700 group-hover:ring-1 group-hover:ring-marca-200">
                          <IconoDocumento className="size-[18px]" />
                        </span>
                        <div className="min-w-0">
                          <p className="max-w-[16rem] truncate font-medium text-slate-900 sm:max-w-xs">
                            {documento.nombre_original}
                          </p>
                          <p className="text-xs text-slate-500">
                            {NOMBRES_TIPO[documento.tipo]}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-3 py-3.5">
                      <InsigniaEstado estado={documento.estado} />
                    </td>
                    <td className="hidden px-3 py-3.5 text-slate-600 tabular-nums md:table-cell">
                      {formatearTamano(documento.tamano_bytes)}
                    </td>
                    <td className="px-6 py-3.5 text-right whitespace-nowrap text-slate-600">
                      {formatearFecha(documento.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between border-t border-slate-200/80 px-6 py-3.5 text-sm">
            <span className="text-slate-500">
              <span className="font-medium text-slate-900 tabular-nums">
                {desde}–{hasta}
              </span>{' '}
              de <span className="tabular-nums">{total}</span>
            </span>
            <div className="flex gap-2">
              <Boton
                variante="secundario"
                className="px-2.5 py-1.5"
                onClick={() => setPagina((p) => p - 1)}
                disabled={pagina <= 1}
                aria-label="Página anterior"
              >
                <IconoIzquierda className="size-4" />
              </Boton>
              <Boton
                variante="secundario"
                className="px-2.5 py-1.5"
                onClick={() => setPagina((p) => p + 1)}
                disabled={pagina >= totalPaginas}
                aria-label="Página siguiente"
              >
                <IconoDerecha className="size-4" />
              </Boton>
            </div>
          </div>
        </>
      )}
    </Tarjeta>
  )

  return (
    <>
      <EncabezadoPagina
        titulo="Documentos"
        descripcion={
          esFuncionario
            ? 'Sube PDFs para su revisión y consulta los que ya enviaste.'
            : 'Documentos subidos por el personal para su revisión.'
        }
      />

      {/* Solo el funcionario sube documentos (el endpoint es SoloFuncionario). */}
      {esFuncionario ? (
        <div className="grid items-start gap-6 lg:grid-cols-[22rem_1fr]">
          <FormularioSubida />
          {lista}
        </div>
      ) : (
        lista
      )}
    </>
  )
}
