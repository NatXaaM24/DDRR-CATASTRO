import { useState } from 'react'
import { Navigate } from 'react-router'
import { PantallaDeCarga } from '../../components/Estados'
import { IconoCandado, IconoEscudo, IconoHuella } from '../../components/Iconos'
import { Marca } from '../../components/Marca'
import { FormularioCredenciales } from './FormularioCredenciales'
import { PasoBiometrico } from './PasoBiometrico'
import { useSesion } from './useSesion'

type Paso =
  | { tipo: 'credenciales' }
  | { tipo: 'biometria'; preauthToken: string; tieneCredencial: boolean }

const GARANTIAS = [
  {
    icono: IconoCandado,
    titulo: 'Acceso en dos pasos',
    texto: 'Contraseña y verificación biométrica para cada ingreso.',
  },
  {
    icono: IconoEscudo,
    titulo: 'Integridad verificable',
    texto: 'Cada documento conserva su huella SHA-256 desde que se sube.',
  },
  {
    icono: IconoHuella,
    titulo: 'Decisión humana',
    texto: 'El asistente solo recomienda; el personal decide.',
  },
]

function Pasos({ actual }: { actual: 1 | 2 }) {
  const pasos = ['Credenciales', 'Verificación biométrica']
  return (
    <ol className="mb-8 flex items-center gap-3 text-xs font-medium">
      {pasos.map((nombre, i) => {
        const numero = i + 1
        const activo = numero === actual
        const hecho = numero < actual
        return (
          <li key={nombre} className="flex items-center gap-3">
            {i > 0 && <span className="h-px w-6 bg-slate-300" />}
            <span
              className={`flex items-center gap-2 ${activo ? 'text-marca-800' : hecho ? 'text-slate-700' : 'text-slate-400'}`}
            >
              <span
                className={`flex size-6 items-center justify-center rounded-full text-[11px] ring-1 ${
                  activo
                    ? 'bg-marca-700 text-white ring-marca-700'
                    : hecho
                      ? 'bg-marca-50 text-marca-800 ring-marca-200'
                      : 'bg-white text-slate-400 ring-slate-300'
                }`}
              >
                {numero}
              </span>
              {nombre}
            </span>
          </li>
        )
      })}
    </ol>
  )
}

export function LoginPage() {
  const { estado } = useSesion()
  const [paso, setPaso] = useState<Paso>({ tipo: 'credenciales' })

  if (estado === 'cargando') return <PantallaDeCarga />
  if (estado === 'autenticado') return <Navigate to="/" replace />

  const esCredenciales = paso.tipo === 'credenciales'

  return (
    <main className="grid min-h-screen lg:grid-cols-[1.05fr_1fr]">
      {/* Panel institucional. */}
      <section className="relative hidden overflow-hidden bg-marca-900 lg:flex lg:flex-col lg:justify-between lg:p-12">
        <svg
          className="pointer-events-none absolute inset-0 size-full opacity-[0.07]"
          aria-hidden="true"
        >
          <defs>
            <pattern
              id="cuadricula"
              width="56"
              height="56"
              patternUnits="userSpaceOnUse"
            >
              <path d="M56 0H0v56" fill="none" stroke="white" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#cuadricula)" />
        </svg>
        <div className="pointer-events-none absolute -right-32 -bottom-32 size-[28rem] rounded-full bg-marca-600/30 blur-3xl" />

        <div className="relative">
          <Marca claro />
        </div>

        <div className="relative max-w-md">
          <h2 className="text-3xl leading-tight font-semibold tracking-tight text-white xl:text-4xl">
            Revisión de documentos de Derechos Reales y Catastro.
          </h2>
          <p className="mt-4 text-base leading-relaxed text-marca-200">
            Una plataforma para que el personal revise, compare y certifique
            documentos de registro de bienes inmuebles.
          </p>

          <ul className="mt-10 space-y-5">
            {GARANTIAS.map(({ icono: Icono, titulo, texto }) => (
              <li key={titulo} className="flex gap-4">
                <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-white/10 text-white ring-1 ring-white/15">
                  <Icono className="size-5" />
                </span>
                <span>
                  <span className="block text-sm font-medium text-white">
                    {titulo}
                  </span>
                  <span className="block text-sm text-marca-200">{texto}</span>
                </span>
              </li>
            ))}
          </ul>
        </div>

        <p className="relative text-xs text-marca-300">
          Uso exclusivo del personal autorizado.
        </p>
      </section>

      {/* Formulario. */}
      <section className="flex items-center justify-center px-4 py-12 sm:px-8">
        <div className="w-full max-w-sm">
          <div className="mb-10 lg:hidden">
            <Marca />
          </div>

          <Pasos actual={esCredenciales ? 1 : 2} />

          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
            {esCredenciales ? 'Iniciar sesión' : 'Verifica tu identidad'}
          </h1>
          <p className="mt-1.5 mb-8 text-sm text-slate-500">
            {esCredenciales
              ? 'Ingresa con tu usuario y contraseña institucionales.'
              : 'Usa la huella, el rostro o el PIN de tu dispositivo.'}
          </p>

          {paso.tipo === 'credenciales' ? (
            <FormularioCredenciales
              onExito={(preauthToken, tieneCredencial) =>
                setPaso({ tipo: 'biometria', preauthToken, tieneCredencial })
              }
            />
          ) : (
            <PasoBiometrico
              preauthToken={paso.preauthToken}
              tieneCredencial={paso.tieneCredencial}
              onVolver={() => setPaso({ tipo: 'credenciales' })}
            />
          )}
        </div>
      </section>
    </main>
  )
}
