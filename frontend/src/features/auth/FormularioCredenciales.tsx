import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import {
  Aviso,
  Boton,
  ErrorCampo,
  Etiqueta,
  Girador,
} from '../../components/ui'
import { clasesCampo } from '../../components/estilos'
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
      className="space-y-5"
    >
      <div>
        <Etiqueta htmlFor="username">Usuario</Etiqueta>
        <input
          id="username"
          type="text"
          autoComplete="username"
          aria-invalid={errors.username ? true : undefined}
          className={clasesCampo}
          {...register('username')}
        />
        <ErrorCampo mensaje={errors.username?.message} />
      </div>

      <div>
        <Etiqueta htmlFor="password">Contraseña</Etiqueta>
        <input
          id="password"
          type="password"
          autoComplete="current-password"
          aria-invalid={errors.password ? true : undefined}
          className={clasesCampo}
          {...register('password')}
        />
        <ErrorCampo mensaje={errors.password?.message} />
      </div>

      {mensajeError && <Aviso tipo="error">{mensajeError}</Aviso>}

      <Boton type="submit" ancho disabled={login.isPending}>
        {login.isPending && <Girador className="size-4" />}
        {login.isPending ? 'Verificando…' : 'Continuar'}
      </Boton>
    </form>
  )
}
