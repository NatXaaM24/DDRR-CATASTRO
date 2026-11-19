interface Props {
  claro?: boolean
}

// Emblema: una parcela dividida en lotes, sobre un sello cuadrado.
export function Emblema({ className = 'size-9' }: { className?: string }) {
  return (
    <svg viewBox="0 0 40 40" className={className} aria-hidden="true">
      <rect width="40" height="40" rx="10" className="fill-marca-700" />
      <path
        d="M11 12.5 27.5 10 30 27.5 13.5 30z"
        fill="none"
        stroke="white"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      <path
        d="M19.3 11.3 21.8 28.8M12.3 21.3l16.5-2.5"
        stroke="white"
        strokeOpacity=".55"
        strokeWidth="1.5"
      />
    </svg>
  )
}

export function Marca({ claro = false }: Props) {
  return (
    <div className="flex items-center gap-3">
      <Emblema />
      <div className="leading-tight">
        <p
          className={`text-[15px] font-semibold tracking-tight ${claro ? 'text-white' : 'text-slate-900'}`}
        >
          DDRR · Catastro
        </p>
        <p className={`text-xs ${claro ? 'text-marca-200' : 'text-slate-500'}`}>
          Cochabamba
        </p>
      </div>
    </div>
  )
}
