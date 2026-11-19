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
