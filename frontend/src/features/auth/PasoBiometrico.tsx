interface Props {
  preauthToken: string
  tieneCredencial: boolean
  onVolver: () => void
}

// Provisional: la biometría real (WebAuthn) se escribe en la pieza 5.
export function PasoBiometrico({ tieneCredencial, onVolver }: Props) {
  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-700">
        Contraseña correcta.{' '}
        {tieneCredencial
          ? 'Falta verificar tu dispositivo.'
          : 'Falta registrar tu dispositivo.'}
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
