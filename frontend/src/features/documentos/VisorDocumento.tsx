import { useQuery } from '@tanstack/react-query'
import { useEffect, useRef, useState, type ReactNode } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/Page/TextLayer.css'
import 'react-pdf/dist/Page/AnnotationLayer.css'
import { Link, useParams } from 'react-router'
import {
  IconoDerecha,
  IconoEscudo,
  IconoIzquierda,
} from '../../components/Iconos'
import { Aviso, Boton, Girador, Tarjeta } from '../../components/ui'
import { ErrorApi } from '../../lib/api'
import { descargarPdf, obtenerDocumento } from './api'
import { formatearFecha, formatearTamano } from './formato'
import { InsigniaEstado } from './InsigniaEstado'
import { NOMBRES_TIPO } from './types'

// El worker de pdf.js se sirve desde el propio bundle (sin CDN).
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString()

function mensajeDe(error: unknown, generico: string): string {
  return error instanceof ErrorApi ? error.message : generico
}

// Ancho disponible del contenedor, para que la página del PDF lo ocupe.
function useAncho<T extends HTMLElement>() {
  const ref = useRef<T>(null)
  const [ancho, setAncho] = useState(0)
  useEffect(() => {
    const elemento = ref.current
    if (!elemento) return
    const observador = new ResizeObserver(([entrada]) => {
      setAncho(Math.floor(entrada.contentRect.width))
    })
    observador.observe(elemento)
    return () => observador.disconnect()
  }, [])
  return [ref, ancho] as const
}

function Dato({
  etiqueta,
  children,
}: {
  etiqueta: string
  children: ReactNode
}) {
  return (
    <div className="py-3.5">
      <dt className="text-xs font-medium tracking-wide text-slate-500 uppercase">
        {etiqueta}
      </dt>
      <dd className="mt-1 text-sm text-slate-900">{children}</dd>
    </div>
  )
}

function Cargando({ texto }: { texto: string }) {
  return (
    <div
      role="status"
      className="flex items-center justify-center gap-2.5 py-24 text-sm text-slate-500"
    >
      <Girador className="size-4 text-marca-600" />
      {texto}
    </div>
  )
}

export function VisorDocumento() {
  const { id = '' } = useParams()
  const [numPaginas, setNumPaginas] = useState(0)
  const [pagina, setPagina] = useState(1)
  const [refLienzo, anchoLienzo] = useAncho<HTMLDivElement>()

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

  const documento = detalle.data

  return (
    <>
      <Link
        to="/documentos"
        className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 transition-colors hover:text-marca-700"
      >
        <IconoIzquierda className="size-4" />
        Documentos
      </Link>

      <div className="mt-3 mb-8 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="min-w-0 truncate text-2xl font-semibold tracking-tight text-slate-900 sm:text-[28px]">
          {documento?.nombre_original ?? 'Documento'}
        </h1>
        {documento && <InsigniaEstado estado={documento.estado} />}
      </div>

      {detalle.isError && (
        <div className="mb-6">
          <Aviso tipo="error">
            {mensajeDe(detalle.error, 'No se pudo cargar el documento.')}
          </Aviso>
        </div>
      )}

      <div className="grid items-start gap-6 lg:grid-cols-[1fr_20rem]">
        {/* Visor. */}
        <Tarjeta className="overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-200/80 px-4 py-3">
            <span className="text-sm text-slate-500">
              {numPaginas > 0 ? (
                <>
                  Página{' '}
                  <span className="font-medium text-slate-900 tabular-nums">
                    {pagina}
                  </span>{' '}
                  de <span className="tabular-nums">{numPaginas}</span>
                </>
              ) : (
                'Vista previa'
              )}
            </span>
            <div className="flex gap-2">
              <Boton
                variante="secundario"
                className="px-2.5 py-1.5"
                onClick={() => setPagina((p) => p - 1)}
                disabled={pagina <= 1 || numPaginas === 0}
                aria-label="Página anterior"
              >
                <IconoIzquierda className="size-4" />
              </Boton>
              <Boton
                variante="secundario"
                className="px-2.5 py-1.5"
                onClick={() => setPagina((p) => p + 1)}
                disabled={pagina >= numPaginas}
                aria-label="Página siguiente"
              >
                <IconoDerecha className="size-4" />
              </Boton>
            </div>
          </div>

          <div className="bg-slate-100/70 p-4 sm:p-6">
            <div ref={refLienzo} className="mx-auto max-w-3xl">
              {pdf.isPending && <Cargando texto="Cargando PDF…" />}
              {pdf.isError && (
                <Aviso tipo="error">
                  {mensajeDe(pdf.error, 'No se pudo cargar el PDF.')}
                </Aviso>
              )}
              {pdf.data && (
                <Document
                  file={pdf.data}
                  onLoadSuccess={({ numPages }) => {
                    setNumPaginas(numPages)
                    setPagina(1)
                  }}
                  loading={<Cargando texto="Abriendo PDF…" />}
                  error={<Aviso tipo="error">No se pudo mostrar el PDF.</Aviso>}
                >
                  <Page
                    pageNumber={pagina}
                    width={anchoLienzo || undefined}
                    loading={<Cargando texto="Dibujando página…" />}
                    className="overflow-hidden rounded-sm shadow-lg ring-1 ring-slate-900/5"
                  />
                </Document>
              )}
            </div>
          </div>
        </Tarjeta>

        {/* Detalle. */}
        <Tarjeta className="px-6 py-2">
          {detalle.isPending && <Cargando texto="Cargando datos…" />}
          {documento && (
            <dl className="divide-y divide-slate-100">
              <Dato etiqueta="Tipo">{NOMBRES_TIPO[documento.tipo]}</Dato>
              <Dato etiqueta="Tamaño">
                <span className="tabular-nums">
                  {formatearTamano(documento.tamano_bytes)}
                </span>
              </Dato>
              <Dato etiqueta="Subido">
                {formatearFecha(documento.created_at)}
              </Dato>
              <Dato etiqueta="Huella SHA-256">
                <span className="block font-mono text-xs leading-relaxed break-all text-slate-700">
                  {documento.hash_sha256}
                </span>
              </Dato>
              {pdf.data && (
                <div className="py-3.5">
                  <p className="flex items-center gap-2 text-sm font-medium text-emerald-700">
                    <IconoEscudo className="size-4" />
                    Integridad verificada
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    El servidor recalculó la huella al abrir el archivo.
                  </p>
                </div>
              )}
            </dl>
          )}
        </Tarjeta>
      </div>
    </>
  )
}
