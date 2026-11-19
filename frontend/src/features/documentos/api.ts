import { api } from '../../lib/api'
import type { Documento, Pagina, TipoDocumento } from './types'

export const TAMANO_PAGINA = 20

export function listarDocumentos(pagina: number): Promise<Pagina<Documento>> {
  const parametros = new URLSearchParams({
    pagina: String(pagina),
    tamano: String(TAMANO_PAGINA),
  })
  return api<Pagina<Documento>>(`/documentos?${parametros.toString()}`)
}

export function subirDocumento(
  archivo: File,
  tipo: TipoDocumento,
): Promise<Documento> {
  const formulario = new FormData()
  formulario.append('archivo', archivo)
  formulario.append('tipo', tipo)
  return api<Documento>('/documentos', { metodo: 'POST', cuerpo: formulario })
}

export function obtenerDocumento(id: string): Promise<Documento> {
  return api<Documento>(`/documentos/${encodeURIComponent(id)}`)
}

// El PDF se pide con el token en la cabecera (no por URL), así que llega como Blob.
export function descargarPdf(id: string): Promise<Blob> {
  return api<Blob>(`/documentos/${encodeURIComponent(id)}/pdf`, {
    formato: 'blob',
  })
}
