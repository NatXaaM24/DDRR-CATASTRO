import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { ErrorApi } from '../../lib/api'
import { subirDocumento } from './api'
import { NOMBRES_TIPO, type TipoDocumento } from './types'

const TIPOS = Object.keys(NOMBRES_TIPO) as [TipoDocumento, ...TipoDocumento[]]

// El tipo real y el tamaño máximo los valida el servidor (R-SEG-7);
// aquí solo se evita enviar algo que claramente no es un PDF.
const esquema = z.object({
  tipo: z.enum(TIPOS, { message: 'Elige el tipo de documento.' }),
  archivos: z
    .custom<FileList>()
    .refine((lista) => lista instanceof FileList && lista.length === 1, {
      message: 'Elige un archivo PDF.',
    })
    .refine(
      (lista) =>
        lista instanceof FileList &&
        lista.length === 1 &&
        lista[0].name.toLowerCase().endsWith('.pdf'),
      { message: 'Solo se aceptan archivos PDF.' },
    ),
})

type Datos = z.infer<typeof esquema>

export function FormularioSubida() {
  const queryClient = useQueryClient()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<Datos>({ resolver: zodResolver(esquema) })

  const subida = useMutation({
    mutationFn: (datos: Datos) => subirDocumento(datos.archivos[0], datos.tipo),
    onSuccess: () => {
      reset()
      void queryClient.invalidateQueries({ queryKey: ['documentos'] })
    },
  })

  let mensajeError: string | null = null
  if (subida.error instanceof ErrorApi) mensajeError = subida.error.message
  else if (subida.error) mensajeError = 'Ocurrió un error inesperado.'

  return (
    <form
      onSubmit={handleSubmit((datos) => subida.mutate(datos))}
      noValidate
      className="space-y-4 rounded-lg border border-slate-200 p-4"
    >
      <h2 className="text-lg font-semibold text-slate-900">Subir documento</h2>

      <div>
        <label
          htmlFor="tipo"
          className="block text-sm font-medium text-slate-700"
        >
          Tipo
        </label>
        <select
          id="tipo"
          defaultValue=""
          aria-invalid={errors.tipo ? true : undefined}
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 focus:border-blue-600 focus:outline-none focus:ring-1 focus:ring-blue-600"
          {...register('tipo')}
        >
          <option value="" disabled>
            Elige un tipo…
          </option>
          {TIPOS.map((tipo) => (
            <option key={tipo} value={tipo}>
              {NOMBRES_TIPO[tipo]}
            </option>
          ))}
        </select>
        {errors.tipo && (
          <p role="alert" className="mt-1 text-sm text-red-600">
            {errors.tipo.message}
          </p>
        )}
      </div>

      <div>
        <label
          htmlFor="archivo"
          className="block text-sm font-medium text-slate-700"
        >
          Archivo PDF
        </label>
        <input
          id="archivo"
          type="file"
          accept="application/pdf,.pdf"
          aria-invalid={errors.archivos ? true : undefined}
          className="mt-1 block w-full text-sm text-slate-700"
          {...register('archivos')}
        />
        {errors.archivos && (
          <p role="alert" className="mt-1 text-sm text-red-600">
            {errors.archivos.message}
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
      {subida.isSuccess && (
        <p role="status" className="text-sm text-green-700">
          Documento subido.
        </p>
      )}

      <button
        type="submit"
        disabled={subida.isPending}
        className="rounded-md bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-60"
      >
        {subida.isPending ? 'Subiendo…' : 'Subir'}
      </button>
    </form>
  )
}
