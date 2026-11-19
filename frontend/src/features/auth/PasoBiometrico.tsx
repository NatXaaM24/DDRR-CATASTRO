import { zodResolver } from '@hookform/resolvers/zod'
import {
  browserSupportsWebAuthn,
  startAuthentication,
  startRegistration,
} from '@simplewebauthn/browser'
import { useMutation } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { IconoHuella } from '../../components/Iconos'
import {
  Aviso,
  Boton,
  ErrorCampo,
  Etiqueta,
  Girador,
} from '../../components/ui'
import { clasesCampo } from '../../components/estilos'
import { ErrorApi } from '../../lib/api'
import {
  pedirOpcionesAutenticacion,
  pedirOpcionesRegistro,
  verificarAutenticacion,
  verificarRegistro,
} from './api'
import type { TokenSalida } from './types'
import { useSesion } from './useSesion'

const esquema = z.object({
  nombre: z
    .string()
    .trim()
    .min(1, 'Ponle un nombre a tu dispositivo.')
    .max(100, 'Máximo 100 caracteres.'),
})

type Datos = z.infer<typeof esquema>

interface Props {
  preauthToken: string
  tieneCredencial: boolean
  onVolver: () => void
}

function mensajeDeError(error: unknown): string {
  if (error instanceof ErrorApi) return error.message
  if (error instanceof Error) {
    if (error.name === 'NotAllowedError') {
      return 'La verificación se canceló o tardó demasiado. Inténtalo de nuevo.'
    }
    if (error.name === 'InvalidStateError') {
      return 'Este dispositivo ya está registrado.'
    }
  }
  return 'No se pudo completar la verificación del dispositivo.'
}

export function PasoBiometrico({
  preauthToken,
  tieneCredencial,
  onVolver,
}: Props) {
  const { iniciarSesion } = useSesion()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<Datos>({
    resolver: zodResolver(esquema),
    defaultValues: { nombre: 'Mi dispositivo' },
  })

  const verificar = useMutation({
    mutationFn: async (datos: Datos): Promise<TokenSalida> => {
      if (tieneCredencial) {
        const opciones = await pedirOpcionesAutenticacion(preauthToken)
        const credencial = await startAuthentication({ optionsJSON: opciones })
        return verificarAutenticacion(preauthToken, credencial)
      }
      const opciones = await pedirOpcionesRegistro(preauthToken)
      const credencial = await startRegistration({ optionsJSON: opciones })
      return verificarRegistro(preauthToken, credencial, datos.nombre)
    },
    onSuccess: (tokens) => iniciarSesion(tokens),
  })

  if (!browserSupportsWebAuthn()) {
    return (
      <div className="space-y-5">
        <Aviso tipo="error">
          Este navegador no permite la verificación biométrica. Usa una versión
          reciente de Chrome, Edge o Firefox, desde http://localhost:5173.
        </Aviso>
        <Boton variante="secundario" ancho onClick={onVolver}>
          Volver
        </Boton>
      </div>
    )
  }

  return (
    <form
      onSubmit={handleSubmit((datos) => verificar.mutate(datos))}
      noValidate
      className="space-y-5"
    >
      <div className="flex items-start gap-4 rounded-xl bg-marca-50 p-4 ring-1 ring-marca-100">
        <span className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-white text-marca-700 shadow-xs ring-1 ring-marca-200">
          <IconoHuella
            className={`size-6 ${verificar.isPending ? 'animate-pulse' : ''}`}
          />
        </span>
        <p className="text-sm leading-relaxed text-marca-900">
          {tieneCredencial
            ? 'Contraseña correcta. Confirma que eres tú con la huella, el rostro o el PIN de tu dispositivo.'
            : 'Contraseña correcta. Para entrar, registra primero tu dispositivo (huella, rostro o PIN).'}
        </p>
      </div>

      {!tieneCredencial && (
        <div>
          <Etiqueta htmlFor="nombre">Nombre del dispositivo</Etiqueta>
          <input
            id="nombre"
            type="text"
            aria-invalid={errors.nombre ? true : undefined}
            className={clasesCampo}
            {...register('nombre')}
          />
          <ErrorCampo mensaje={errors.nombre?.message} />
        </div>
      )}

      {verificar.error && (
        <Aviso tipo="error">{mensajeDeError(verificar.error)}</Aviso>
      )}

      <div className="space-y-3">
        <Boton type="submit" ancho disabled={verificar.isPending}>
          {verificar.isPending && <Girador className="size-4" />}
          {verificar.isPending
            ? 'Esperando a tu dispositivo…'
            : tieneCredencial
              ? 'Verificar con mi dispositivo'
              : 'Registrar mi dispositivo'}
        </Boton>
        <Boton variante="fantasma" ancho onClick={onVolver}>
          Volver
        </Boton>
      </div>
    </form>
  )
}
