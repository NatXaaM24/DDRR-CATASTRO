import { useState } from 'react'
import { Navigate } from 'react-router'
import { PantallaDeCarga } from '../../components/Estados'
import { FormularioCredenciales } from './FormularioCredenciales'
import { PasoBiometrico } from './PasoBiometrico'
import { useSesion } from './useSesion'

type Paso =
  | { tipo: 'credenciales' }
  | { tipo: 'biometria'; preauthToken: string; tieneCredencial: boolean }

export function LoginPage() {
  const { estado } = useSesion()
  const [paso, setPaso] = useState<Paso>({ tipo: 'credenciales' })

  if (estado === 'cargando') return <PantallaDeCarga />
  if (estado === 'autenticado') return <Navigate to="/" replace />

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
      <div className="w-full max-w-sm rounded-xl bg-white p-6 shadow">
        <h1 className="text-xl font-semibold text-slate-900">DDRR–Catastro</h1>
        <p className="mb-6 text-sm text-slate-600">
          Inicia sesión para continuar.
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
    </main>
  )
}
