export function PantallaDeCarga() {
  return (
    <main
      role="status"
      className="flex min-h-screen items-center justify-center text-slate-600"
    >
      Cargando…
    </main>
  )
}

export function SinPermiso() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-2 px-4 text-center">
      <h1 className="text-xl font-semibold text-slate-900">Sin permiso</h1>
      <p className="text-slate-600">No tienes permiso para ver esta página.</p>
    </main>
  )
}
