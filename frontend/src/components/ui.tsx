// Piezas visuales compartidas. Solo estilos: sin lógica de negocio.
import type {
  ButtonHTMLAttributes,
  ComponentType,
  ReactNode,
  SVGProps,
} from 'react'
import { clasesBoton, type Variante } from './estilos'
import { IconoAlerta, IconoCheck } from './Iconos'

interface PropsBoton extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: Variante
  ancho?: boolean
}

export function Boton({
  variante = 'primario',
  ancho = false,
  className = '',
  type = 'button',
  ...props
}: PropsBoton) {
  return (
    <button
      type={type}
      className={`${clasesBoton(variante, ancho)} ${className}`}
      {...props}
    />
  )
}

export function Etiqueta({
  htmlFor,
  children,
}: {
  htmlFor: string
  children: ReactNode
}) {
  return (
    <label
      htmlFor={htmlFor}
      className="mb-1.5 block text-sm font-medium text-slate-700"
    >
      {children}
    </label>
  )
}

export function ErrorCampo({ mensaje }: { mensaje?: string }) {
  if (!mensaje) return null
  return (
    <p role="alert" className="mt-1.5 text-sm text-red-600">
      {mensaje}
    </p>
  )
}

export function Aviso({
  tipo,
  children,
}: {
  tipo: 'error' | 'exito'
  children: ReactNode
}) {
  const error = tipo === 'error'
  const Icono = error ? IconoAlerta : IconoCheck
  return (
    <div
      role={error ? 'alert' : 'status'}
      className={`flex items-start gap-2.5 rounded-lg px-3.5 py-3 text-sm ring-1 ring-inset ${
        error
          ? 'bg-red-50 text-red-800 ring-red-200'
          : 'bg-emerald-50 text-emerald-800 ring-emerald-200'
      }`}
    >
      <Icono className="mt-px size-4 shrink-0" />
      <div>{children}</div>
    </div>
  )
}

export function Tarjeta({
  children,
  className = '',
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <section
      className={`rounded-2xl bg-white shadow-xs ring-1 ring-slate-200/80 ${className}`}
    >
      {children}
    </section>
  )
}

export function EncabezadoPagina({
  titulo,
  descripcion,
  acciones,
}: {
  titulo: ReactNode
  descripcion?: ReactNode
  acciones?: ReactNode
}) {
  return (
    <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div className="min-w-0">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900 sm:text-[28px]">
          {titulo}
        </h1>
        {descripcion && (
          <p className="mt-1.5 text-sm text-slate-500">{descripcion}</p>
        )}
      </div>
      {acciones && <div className="shrink-0">{acciones}</div>}
    </div>
  )
}

export type Tono = 'neutro' | 'marca' | 'ambar' | 'verde' | 'rojo'

const TONOS: Record<Tono, string> = {
  neutro: 'bg-slate-100 text-slate-700 ring-slate-200',
  marca: 'bg-marca-50 text-marca-800 ring-marca-200',
  ambar: 'bg-amber-50 text-amber-800 ring-amber-200',
  verde: 'bg-emerald-50 text-emerald-800 ring-emerald-200',
  rojo: 'bg-red-50 text-red-800 ring-red-200',
}

export function Insignia({
  tono = 'neutro',
  children,
}: {
  tono?: Tono
  children: ReactNode
}) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium whitespace-nowrap ring-1 ring-inset ${TONOS[tono]}`}
    >
      <span className="size-1.5 rounded-full bg-current opacity-70" />
      {children}
    </span>
  )
}

export function Girador({ className = 'size-5' }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      className={`animate-spin ${className}`}
      aria-hidden="true"
    >
      <circle
        cx="12"
        cy="12"
        r="9"
        fill="none"
        stroke="currentColor"
        strokeOpacity=".2"
        strokeWidth="2.5"
      />
      <path
        d="M21 12a9 9 0 0 0-9-9"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
    </svg>
  )
}

export function EstadoVacio({
  icono: Icono,
  titulo,
  descripcion,
}: {
  icono: ComponentType<SVGProps<SVGSVGElement>>
  titulo: string
  descripcion?: string
}) {
  return (
    <div className="flex flex-col items-center px-6 py-14 text-center">
      <div className="flex size-12 items-center justify-center rounded-xl bg-slate-100 text-slate-400">
        <Icono className="size-6" />
      </div>
      <p className="mt-4 text-sm font-medium text-slate-900">{titulo}</p>
      {descripcion && (
        <p className="mt-1 max-w-sm text-sm text-slate-500">{descripcion}</p>
      )}
    </div>
  )
}
