import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router'
import { ErrorApi } from '../../lib/api'
import { useSesion } from '../auth/useSesion'
import { TAMANO_PAGINA, listarDocumentos } from './api'
import { FormularioSubida } from './FormularioSubida'
import { NOMBRES_ESTADO, NOMBRES_TIPO } from './types'

const fecha = new Intl.DateTimeFormat('es-BO', {
  dateStyle: 'short',
  timeStyle: 'short',
})

function formatearTamano(bytes: number): string {
  if (bytes < 1024 * 1024) return `${Math.ceil(bytes / 1024)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export function PaginaDocumentos() {
  const { usuario } = useSesion()
  const [pagina, setPagina] = useState(1)

  const consulta = useQuery({
    queryKey: ['documentos', pagina],
    queryFn: () => listarDocumentos(pagina),
    placeholderData: keepPreviousData,
  })

  const totalPaginas = consulta.data
    ? Math.max(1, Math.ceil(consulta.data.total / TAMANO_PAGINA))
    : 1

  return (
    <main className="mx-auto max-w-5xl space-y-6 px-4 py-10">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900">Documentos</h1>
        <Link to="/" className="text-sm text-blue-700 hover:underline">
          Volver al inicio
        </Link>
      </div>

      {/* Solo el funcionario sube documentos (el endpoint es SoloFuncionario). */}
      {usuario?.rol === 'funcionario' && <FormularioSubida />}

      {consulta.isPending && (
        <p role="status" className="text-slate-600">
          Cargando documentos…
        </p>
      )}
      {consulta.isError && (
        <p
          role="alert"
          className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          {consulta.error instanceof ErrorApi
            ? consulta.error.message
            : 'No se pudieron cargar los documentos.'}
        </p>
      )}

      {consulta.data && consulta.data.items.length === 0 && (
        <p className="text-slate-600">No hay documentos.</p>
      )}

      {consulta.data && consulta.data.items.length > 0 && (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-200 text-slate-600">
                <tr>
                  <th className="py-2 pr-4 font-medium">Nombre</th>
                  <th className="py-2 pr-4 font-medium">Tipo</th>
                  <th className="py-2 pr-4 font-medium">Estado</th>
                  <th className="py-2 pr-4 font-medium">Tamaño</th>
                  <th className="py-2 font-medium">Subido</th>
                </tr>
              </thead>
              <tbody>
                {consulta.data.items.map((documento) => (
                  <tr
                    key={documento.id}
                    className="border-b border-slate-100 text-slate-800"
                  >
                    <td className="py-2 pr-4 break-all">
                      <Link
                        to={`/documentos/${documento.id}`}
                        className="text-blue-700 hover:underline"
                      >
                        {documento.nombre_original}
                      </Link>
                    </td>
                    <td className="py-2 pr-4">
                      {NOMBRES_TIPO[documento.tipo]}
                    </td>
                    <td className="py-2 pr-4">
                      {NOMBRES_ESTADO[documento.estado]}
                    </td>
                    <td className="py-2 pr-4">
                      {formatearTamano(documento.tamano_bytes)}
                    </td>
                    <td className="py-2">
                      {fecha.format(new Date(documento.created_at))}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between text-sm text-slate-600">
            <span>
              Página {pagina} de {totalPaginas} · {consulta.data.total}{' '}
              documento(s)
            </span>
            <div className="space-x-2">
              <button
                type="button"
                onClick={() => setPagina((p) => p - 1)}
                disabled={pagina <= 1}
                className="rounded-md border border-slate-300 px-3 py-1 hover:bg-slate-50 disabled:opacity-50"
              >
                Anterior
              </button>
              <button
                type="button"
                onClick={() => setPagina((p) => p + 1)}
                disabled={pagina >= totalPaginas}
                className="rounded-md border border-slate-300 px-3 py-1 hover:bg-slate-50 disabled:opacity-50"
              >
                Siguiente
              </button>
            </div>
          </div>
        </>
      )}
    </main>
  )
}
