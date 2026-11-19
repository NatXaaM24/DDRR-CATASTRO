import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useForm, useWatch } from 'react-hook-form'
import { z } from 'zod'
import { IconoDocumento, IconoSubir } from '../../components/Iconos'
import {
  Aviso,
  Boton,
  ErrorCampo,
  Etiqueta,
  Girador,
  Tarjeta,
} from '../../components/ui'
import { clasesCampo } from '../../components/estilos'
import { ErrorApi } from '../../lib/api'
import { subirDocumento } from './api'
import { formatearTamano } from './formato'
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
  const [arrastrando, setArrastrando] = useState(false)
  const {
    register,
    handleSubmit,
    reset,
    setValue,
    control,
    formState: { errors },
  } = useForm<Datos>({ resolver: zodResolver(esquema) })

  const subida = useMutation({
    mutationFn: (datos: Datos) => subirDocumento(datos.archivos[0], datos.tipo),
    onSuccess: () => {
      reset()
      void queryClient.invalidateQueries({ queryKey: ['documentos'] })
    },
  })

  const archivos = useWatch({ control, name: 'archivos' })
  const elegido =
    archivos instanceof FileList && archivos.length > 0 ? archivos[0] : null

  let mensajeError: string | null = null
  if (subida.error instanceof ErrorApi) mensajeError = subida.error.message
  else if (subida.error) mensajeError = 'Ocurrió un error inesperado.'

  return (
    <Tarjeta className="p-6">
      <h2 className="text-base font-semibold text-slate-900">
        Subir documento
      </h2>
      <p className="mt-1 text-sm text-slate-500">
        Solo PDF. Se calcula su huella SHA-256 al guardarlo.
      </p>

      <form
        onSubmit={handleSubmit((datos) => subida.mutate(datos))}
        noValidate
        className="mt-6 space-y-5"
      >
        <div>
          <Etiqueta htmlFor="tipo">Tipo de documento</Etiqueta>
          <select
            id="tipo"
            defaultValue=""
            aria-invalid={errors.tipo ? true : undefined}
            className={clasesCampo}
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
          <ErrorCampo mensaje={errors.tipo?.message} />
        </div>

        <div>
          <span className="mb-1.5 block text-sm font-medium text-slate-700">
            Archivo
          </span>
          <label
            htmlFor="archivo"
            onDragOver={(e) => {
              e.preventDefault()
              setArrastrando(true)
            }}
            onDragLeave={() => setArrastrando(false)}
            onDrop={(e) => {
              e.preventDefault()
              setArrastrando(false)
              setValue('archivos', e.dataTransfer.files, {
                shouldValidate: true,
              })
            }}
            className={`flex cursor-pointer flex-col items-center rounded-xl border-2 border-dashed px-4 py-7 text-center transition ${
              arrastrando
                ? 'border-marca-500 bg-marca-50'
                : errors.archivos
                  ? 'border-red-300 bg-red-50/40'
                  : 'border-slate-300 bg-slate-50/60 hover:border-marca-400 hover:bg-marca-50/50'
            }`}
          >
            {elegido ? (
              <>
                <span className="flex size-10 items-center justify-center rounded-lg bg-white text-marca-700 shadow-xs ring-1 ring-slate-200">
                  <IconoDocumento className="size-5" />
                </span>
                <span className="mt-3 max-w-full truncate text-sm font-medium text-slate-900">
                  {elegido.name}
                </span>
                <span className="mt-0.5 text-xs text-slate-500">
                  {formatearTamano(elegido.size)} · Haz clic para cambiarlo
                </span>
              </>
            ) : (
              <>
                <span className="flex size-10 items-center justify-center rounded-lg bg-white text-slate-500 shadow-xs ring-1 ring-slate-200">
                  <IconoSubir className="size-5" />
                </span>
                <span className="mt-3 text-sm text-slate-700">
                  <span className="font-medium text-marca-700">
                    Elige un archivo
                  </span>{' '}
                  o arrástralo aquí
                </span>
                <span className="mt-0.5 text-xs text-slate-500">
                  PDF, hasta el tamaño máximo permitido
                </span>
              </>
            )}
            <input
              id="archivo"
              type="file"
              accept="application/pdf,.pdf"
              aria-invalid={errors.archivos ? true : undefined}
              className="sr-only"
              {...register('archivos')}
            />
          </label>
          <ErrorCampo mensaje={errors.archivos?.message} />
        </div>

        {mensajeError && <Aviso tipo="error">{mensajeError}</Aviso>}
        {subida.isSuccess && (
          <Aviso tipo="exito">Documento subido correctamente.</Aviso>
        )}

        <Boton type="submit" ancho disabled={subida.isPending}>
          {subida.isPending ? (
            <Girador className="size-4" />
          ) : (
            <IconoSubir className="size-4" />
          )}
          {subida.isPending ? 'Subiendo…' : 'Subir documento'}
        </Boton>
      </form>
    </Tarjeta>
  )
}
