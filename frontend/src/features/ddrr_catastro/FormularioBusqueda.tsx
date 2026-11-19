import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { clasesCampo } from '../../components/estilos'
import { IconoBuscar } from '../../components/Iconos'
import { Boton, ErrorCampo } from '../../components/ui'

const esquema = z.object({
  valor: z
    .string()
    .trim()
    .min(1, 'Escribe un identificador.')
    .max(30, 'Máximo 30 caracteres.'),
})

type Datos = z.infer<typeof esquema>

interface Props {
  id: string
  etiqueta: string
  ejemplo: string
  valorInicial: string
  buscando: boolean
  onBuscar: (valor: string) => void
}

export function FormularioBusqueda({
  id,
  etiqueta,
  ejemplo,
  valorInicial,
  buscando,
  onBuscar,
}: Props) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<Datos>({
    resolver: zodResolver(esquema),
    defaultValues: { valor: valorInicial },
  })

  return (
    <form
      onSubmit={handleSubmit((datos) => onBuscar(datos.valor))}
      noValidate
      role="search"
    >
      <label htmlFor={id} className="sr-only">
        {etiqueta}
      </label>
      <div className="flex gap-2">
        <div className="relative flex-1">
          <IconoBuscar className="pointer-events-none absolute top-1/2 left-3.5 size-4 -translate-y-1/2 text-slate-400" />
          <input
            id={id}
            type="text"
            autoComplete="off"
            spellCheck={false}
            placeholder={ejemplo}
            aria-invalid={errors.valor ? true : undefined}
            className={`${clasesCampo} pl-10 font-mono`}
            {...register('valor')}
          />
        </div>
        <Boton type="submit" disabled={buscando}>
          Buscar
        </Boton>
      </div>
      <ErrorCampo mensaje={errors.valor?.message} />
    </form>
  )
}
