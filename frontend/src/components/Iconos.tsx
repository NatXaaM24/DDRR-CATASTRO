// Iconos SVG en línea (trazo de 1.75 px, heredan el color del texto).
import type { SVGProps } from 'react'

type Props = SVGProps<SVGSVGElement>

function Base({ children, ...props }: Props) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      width="1em"
      height="1em"
      {...props}
    >
      {children}
    </svg>
  )
}

export function IconoDocumento(props: Props) {
  return (
    <Base {...props}>
      <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
      <path d="M14 3v5h5M9 13h6M9 17h4" />
    </Base>
  )
}

export function IconoSubir(props: Props) {
  return (
    <Base {...props}>
      <path d="M12 16V4M7 9l5-5 5 5" />
      <path d="M4 16v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3" />
    </Base>
  )
}

export function IconoSalir(props: Props) {
  return (
    <Base {...props}>
      <path d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3" />
      <path d="M10 17l-5-5 5-5M5 12h11" />
    </Base>
  )
}

export function IconoInicio(props: Props) {
  return (
    <Base {...props}>
      <path d="M4 10.5 12 4l8 6.5V19a1 1 0 0 1-1 1h-4.5v-6h-5v6H5a1 1 0 0 1-1-1z" />
    </Base>
  )
}

export function IconoIzquierda(props: Props) {
  return (
    <Base {...props}>
      <path d="M15 18l-6-6 6-6" />
    </Base>
  )
}

export function IconoDerecha(props: Props) {
  return (
    <Base {...props}>
      <path d="M9 18l6-6-6-6" />
    </Base>
  )
}

export function IconoHuella(props: Props) {
  return (
    <Base {...props}>
      <path d="M12 11v3a8 8 0 0 1-1.5 4.7" />
      <path d="M8.5 7.6A5 5 0 0 1 17 11v2a12 12 0 0 1-.8 4.3" />
      <path d="M7 11a5 5 0 0 1 .3-1.7M7 14.5a12 12 0 0 1-1 4" />
      <path d="M4.5 9.5A8 8 0 0 1 19.6 8M20 12.5v.5a15 15 0 0 1-.5 3.8" />
      <path d="M13.8 20.5c.4-.9.8-2.1 1-3.5" />
    </Base>
  )
}

export function IconoEscudo(props: Props) {
  return (
    <Base {...props}>
      <path d="M12 3 5 6v5c0 4.4 3 8.3 7 9.5 4-1.2 7-5.1 7-9.5V6z" />
      <path d="m9 12 2 2 4-4" />
    </Base>
  )
}

export function IconoAlerta(props: Props) {
  return (
    <Base {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 8v5M12 16.5v.01" />
    </Base>
  )
}

export function IconoCheck(props: Props) {
  return (
    <Base {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="m8.5 12 2.5 2.5 4.5-5" />
    </Base>
  )
}

export function IconoCandado(props: Props) {
  return (
    <Base {...props}>
      <rect x="5" y="11" width="14" height="9" rx="2" />
      <path d="M8 11V8a4 4 0 0 1 8 0v3" />
    </Base>
  )
}

export function IconoBandeja(props: Props) {
  return (
    <Base {...props}>
      <path d="M3 13h5l1.5 3h5L16 13h5" />
      <path d="M5.5 5h13L21 13v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-5z" />
    </Base>
  )
}

export function IconoBuscar(props: Props) {
  return (
    <Base {...props}>
      <circle cx="11" cy="11" r="6.5" />
      <path d="m20 20-4.4-4.4" />
    </Base>
  )
}

export function IconoMapa(props: Props) {
  return (
    <Base {...props}>
      <path d="M9 4 3.5 6v14L9 18l6 2 5.5-2V4L15 6z" />
      <path d="M9 4v14M15 6v14" />
    </Base>
  )
}

export function IconoLibro(props: Props) {
  return (
    <Base {...props}>
      <path d="M5 4.5A1.5 1.5 0 0 1 6.5 3H19v15H6.5A1.5 1.5 0 0 0 5 19.5z" />
      <path d="M5 19.5A1.5 1.5 0 0 0 6.5 21H19v-3M9 7h6" />
    </Base>
  )
}
