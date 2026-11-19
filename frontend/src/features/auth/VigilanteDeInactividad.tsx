import { useEffect, useRef, useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useIdleTimer } from 'react-idle-timer'
import { IconoAlerta } from '../../components/Iconos'
import { Boton } from '../../components/ui'
import { mantenerSesion } from './api'
import { useSesion } from './useSesion'

// Debe coincidir con INACTIVITY_MINUTES del backend (por defecto, 10).
const MINUTOS = Number(import.meta.env.VITE_INACTIVITY_MINUTES ?? 10)
const TIMEOUT_MS = MINUTOS * 60_000
const AVISO_MS = Math.min(60_000, TIMEOUT_MS / 2) // avisa 1 minuto antes (o la mitad si es corto)
const PING_CADA_MS = TIMEOUT_MS / 2 // mientras haya actividad, avisa al servidor cada 5 min

function AvisoDeCierre({ onContinuar }: { onContinuar: () => void }) {
  const [segundos, setSegundos] = useState(AVISO_MS / 1000)

  useEffect(() => {
    const id = setInterval(() => setSegundos((s) => Math.max(0, s - 1)), 1000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 px-4 backdrop-blur-sm">
      <div
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="titulo-inactividad"
        className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl ring-1 ring-slate-200"
      >
        <div className="flex size-11 items-center justify-center rounded-xl bg-amber-50 text-amber-700 ring-1 ring-amber-200">
          <IconoAlerta className="size-6" />
        </div>
        <h2
          id="titulo-inactividad"
          className="mt-4 text-lg font-semibold tracking-tight text-slate-900"
        >
          ¿Sigues ahí?
        </h2>
        <p className="mt-1.5 text-sm text-slate-500">
          Por seguridad, tu sesión se cerrará en{' '}
          <span className="font-semibold text-slate-900 tabular-nums">
            {segundos} s
          </span>{' '}
          por inactividad.
        </p>
        <Boton ancho className="mt-6" onClick={onContinuar}>
          Seguir conectado
        </Boton>
      </div>
    </div>
  )
}

export function VigilanteDeInactividad() {
  const { cerrarSesion } = useSesion()
  const [aviso, setAviso] = useState(false)
  const ultimoAviso = useRef(0)
  const mantener = useMutation({ mutationFn: mantenerSesion })

  const { activate } = useIdleTimer({
    timeout: TIMEOUT_MS,
    promptBeforeIdle: AVISO_MS,
    throttle: 500,
    onPrompt: () => setAviso(true),
    onActive: () => setAviso(false),
    onIdle: () => {
      setAviso(false)
      void cerrarSesion()
    },
    onAction: () => {
      const ahora = Date.now()
      if (ahora - ultimoAviso.current > PING_CADA_MS) {
        ultimoAviso.current = ahora
        mantener.mutate()
      }
    },
  })

  if (!aviso) return null

  return (
    <AvisoDeCierre
      onContinuar={() => {
        activate() // reinicia el cronómetro del navegador
        mantener.mutate() // y el del servidor
      }}
    />
  )
}
