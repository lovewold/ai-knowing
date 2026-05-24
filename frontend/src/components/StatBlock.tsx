interface StatBlockProps {
  label: string
  value: number | string
  unit?: string
}

export default function StatBlock({ label, value, unit }: StatBlockProps) {
  return (
    <div className="border border-ink p-5 flex flex-col justify-between min-h-[120px] hover:bg-mist transition-colors">
      <span className="text-[10px] font-mono uppercase tracking-widest text-silver">{label}</span>
      <div className="mt-auto">
        <span className="font-serif text-4xl font-semibold tabular-nums">{value}</span>
        {unit && <span className="ml-1 text-sm text-silver font-mono">{unit}</span>}
      </div>
    </div>
  )
}
