import { Insignia, type Tono } from '../../components/ui'
import { NOMBRES_ESTADO, type EstadoDocumento } from './types'

const TONO_ESTADO: Record<EstadoDocumento, Tono> = {
  subido: 'marca',
  en_revision: 'ambar',
  revisado: 'verde',
  revision_manual: 'rojo',
}

export function InsigniaEstado({ estado }: { estado: EstadoDocumento }) {
  return (
    <Insignia tono={TONO_ESTADO[estado]}>{NOMBRES_ESTADO[estado]}</Insignia>
  )
}
