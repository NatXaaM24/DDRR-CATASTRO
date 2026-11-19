export type TipoDocumento =
  | 'testimonio'
  | 'folio_real'
  | 'plano_catastral'
  | 'certificado_catastral'
  | 'otro'

export type EstadoDocumento =
  'subido' | 'en_revision' | 'revisado' | 'revision_manual'

export interface Documento {
  id: string
  tipo: TipoDocumento
  nombre_original: string
  hash_sha256: string
  tamano_bytes: number
  estado: EstadoDocumento
  usuario_id: string
  created_at: string
}

export interface Pagina<T> {
  items: T[]
  total: number
  pagina: number
  tamano: number
}

export const NOMBRES_TIPO: Record<TipoDocumento, string> = {
  testimonio: 'Testimonio',
  folio_real: 'Folio real',
  plano_catastral: 'Plano catastral',
  certificado_catastral: 'Certificado catastral',
  otro: 'Otro',
}

export const NOMBRES_ESTADO: Record<EstadoDocumento, string> = {
  subido: 'Subido',
  en_revision: 'En revisión',
  revisado: 'Revisado',
  revision_manual: 'Revisión manual',
}
