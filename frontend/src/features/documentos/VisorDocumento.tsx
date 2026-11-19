import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/Page/TextLayer.css'
import 'react-pdf/dist/Page/AnnotationLayer.css'
import { Link, useParams } from 'react-router'
import { ErrorApi } from '../../lib/api'
import { descargarPdf, obtenerDocumento } from './api'
import { NOMBRES_ESTADO, NOMBRES_TIPO } from './types'

// El worker de pdf.js se sirve desde el propio bundle (sin CDN).
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString()

function mensajeDe(error: unknown, generico: string): string {
  return error instanceof ErrorApi ? error.message : generico
}

export function VisorDocumento() {
  const { id = '' } = useParams()
  const [numPaginas, setNumPaginas] = useState(0)
  const [pagina, setPagina] = useState(1)

  const detalle = useQuery({
    queryKey: ['documentos', 'detalle', id],
    queryFn: () => obtenerDocumento(id),
  })

  // Cada consulta del PDF verifica la integridad en el servidor: no se guarda en caché.
  const pdf = useQuery({
    queryKey: ['documentos', 'pdf', id],
    queryFn: () => descargarPdf(id),
    gcTime: 0,
  })

  return (
    <main className="mx-auto max-w-5xl space-y-6 px-4 py-10">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold break-all text-slate-900">
          {detalle.data?.nombre_original ?? 'Documento'}
        </h1>
        <Link
          to="/documentos"
          className="shrink-0 text-sm text-blue-700 hover:underline"
        >
          Volver a documentos
        </Link>
      </div>

      {detalle.isError && (
        <p
          role="alert"
          className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          {mensajeDe(detalle.error, 'No se pudo cargar el documento.')}
        </p>
      )}

      {detalle.data && (
        <dl className="grid grid-cols-1 gap-2 text-sm sm:grid-cols-3">
          <div>
            <dt className="text-slate-500">Tipo</dt>
            <dd className="text-slate-900">
              {NOMBRES_TIPO[detalle.data.tipo]}
            </dd>
          </div>
          <div>
            <dt className="text-slate-500">Estado</dt>
            <dd className="text-slate-900">
              {NOMBRES_ESTADO[detalle.data.estado]}
            </dd>
          </div>
          <div>
            <dt className="text-slate-500">SHA-256</dt>
            <dd className="font-mono text-xs break-all text-slate-900">
              {detalle.data.hash_sha256}
            </dd>
          </div>
        </dl>
      )}

      {pdf.isPending && (
        <p role="status" className="text-slate-600">
          Cargando PDF…
        </p>
      )}
      {pdf.isError && (
        <p
          role="alert"
          className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          {mensajeDe(pdf.error, 'No se pudo cargar el PDF.')}
        </p>
      )}

      {pdf.data && (
        <section className="space-y-3">
          {numPaginas > 0 && (
            <div className="flex items-center justify-between text-sm text-slate-600">
              <span>
                Página {pagina} de {numPaginas}
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
                  disabled={pagina >= numPaginas}
                  className="rounded-md border border-slate-300 px-3 py-1 hover:bg-slate-50 disabled:opacity-50"
                >
                  Siguiente
                </button>
              </div>
            </div>
          )}
          <div className="overflow-x-auto rounded-lg border border-slate-200 bg-slate-50 p-2">
            <Document
              file={pdf.data}
              onLoadSuccess={({ numPages }) => {
                setNumPaginas(numPages)
                setPagina(1)
              }}
              loading={<p className="text-slate-600">Abriendo PDF…</p>}
              error={
                <p role="alert" className="text-red-700">
                  No se pudo mostrar el PDF.
                </p>
              }
            >
              <Page pageNumber={pagina} />
            </Document>
          </div>
        </section>
      )}
    </main>
  )
}
