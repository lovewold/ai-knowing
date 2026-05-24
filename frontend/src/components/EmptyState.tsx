interface EmptyStateProps {
  title: string
  description: string
}

export default function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div className="border border-dashed border-ink/30 py-16 px-8 text-center">
      <p className="font-serif text-xl text-ink mb-2">{title}</p>
      <p className="text-sm text-silver max-w-sm mx-auto">{description}</p>
    </div>
  )
}
