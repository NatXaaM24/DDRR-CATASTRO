import { zodResolver } from '@hookform/resolvers/zod'
import {
  browserSupportsWebAuthn,
  startAuthentication,
  startRegistration,
} from '@simplewebauthn/browser'
import { useMutation } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
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
      <div className="space-y-4">
        <p
          role="alert"
          className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          Este navegador no permite la verificación biométrica. Usa una versión
          reciente de Chrome, Edge o Firefox, desde http://localhost:5173.
        </p>
        <button
          type="button"
          onClick={onVolver}
          className="w-full rounded-md border border-slate-300 px-4 py-2 text-slate-700 hover:bg-slate-50"
        >
          Volver
        </button>
      </div>
    )
  }

  return (
    <form
      onSubmit={handleSubmit((datos) => verificar.mutate(datos))}
      noValidate
      className="space-y-4"
    >
      <p className="text-sm text-slate-700">
        {tieneCredencial
          ? 'Contraseña correcta. Verifica tu identidad con tu dispositivo (huella, rostro o PIN).'
          : 'Contraseña correcta. Falta registrar tu dispositivo (huella, rostro o PIN) para poder entrar.'}
      </p>

      {!tieneCredencial && (
        <div>
          <label
            htmlFor="nombre"
            className="block text-sm font-medium text-slate-700"
          >
            Nombre del dispositivo
          </label>
          <input
            id="nombre"
            type="text"
            aria-invalid={errors.nombre ? true : undefined}
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 focus:border-blue-600 focus:outline-none focus:ring-1 focus:ring-blue-600"
            {...register('nombre')}
          />
          {errors.nombre && (
            <p role="alert" className="mt-1 text-sm text-red-600">
              {errors.nombre.message}
            </p>
          )}
        </div>
      )}

      {verificar.error && (
        <p
          role="alert"
          className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          {mensajeDeError(verificar.error)}
        </p>
      )}

      <button
        type="submit"
        disabled={verificar.isPending}
        className="w-full rounded-md bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-60"
      >
        {verificar.isPending
          ? 'Esperando a tu dispositivo…'
          : tieneCredencial
            ? 'Verificar con mi dispositivo'
            : 'Registrar mi dispositivo'}
      </button>

      <button
        type="button"
        onClick={onVolver}
        className="w-full rounded-md border border-slate-300 px-4 py-2 text-slate-700 hover:bg-slate-50"
      >
        Volver
      </button>
    </form>
  )
}
