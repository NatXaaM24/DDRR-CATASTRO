import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { ErrorApi } from '../../lib/api'
import { iniciarLogin } from './api'

const esquema = z.object({
  username: z.string().trim().min(1, 'Ingresa tu usuario.'),
  password: z.string().min(1, 'Ingresa tu contraseña.'),
})

type Datos = z.infer<typeof esquema>

interface Props {
  onExito: (preauthToken: string, tieneCredencial: boolean) => void
}

export function FormularioCredenciales({ onExito }: Props) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<Datos>({ resolver: zodResolver(esquema) })

  const login = useMutation({
    mutationFn: (datos: Datos) => iniciarLogin(datos.username, datos.password),
    onSuccess: (respuesta) =>
      onExito(respuesta.preauth_token, respuesta.tiene_credencial),
  })

  let mensajeError: string | null = null
  if (login.error instanceof ErrorApi) mensajeError = login.error.message
  else if (login.error) mensajeError = 'Ocurrió un error inesperado.'

  return (
    <form
      onSubmit={handleSubmit((datos) => login.mutate(datos))}
      noValidate
      className="space-y-4"
    >
      <div>
        <label
          htmlFor="username"
          className="block text-sm font-medium text-slate-700"
        >
          Usuario
        </label>
        <input
          id="username"
          type="text"
          autoComplete="username"
          aria-invalid={errors.username ? true : undefined}
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 focus:border-blue-600 focus:outline-none focus:ring-1 focus:ring-blue-600"
          {...register('username')}
        />
        {errors.username && (
          <p role="alert" className="mt-1 text-sm text-red-600">
            {errors.username.message}
          </p>
        )}
      </div>

      <div>
        <label
          htmlFor="password"
          className="block text-sm font-medium text-slate-700"
        >
          Contraseña
        </label>
        <input
          id="password"
          type="password"
          autoComplete="current-password"
          aria-invalid={errors.password ? true : undefined}
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 focus:border-blue-600 focus:outline-none focus:ring-1 focus:ring-blue-600"
          {...register('password')}
        />
        {errors.password && (
          <p role="alert" className="mt-1 text-sm text-red-600">
            {errors.password.message}
          </p>
        )}
      </div>

      {mensajeError && (
        <p
          role="alert"
          className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          {mensajeError}
        </p>
      )}

      <button
        type="submit"
        disabled={login.isPending}
        className="w-full rounded-md bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-60"
      >
        {login.isPending ? 'Verificando…' : 'Continuar'}
      </button>
    </form>
  )
}
