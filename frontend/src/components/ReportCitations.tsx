import type { ReportCitation } from '../types'

interface ReportCitationsProps {
  citations: ReportCitation[]
  searchQueries?: string[]
}

export default function ReportCitations({ citations, searchQueries }: ReportCitationsProps) {
  if (!citations.length && !searchQueries?.length) return null

  return (
    <section className="mt-12 pt-8 border-t border-ink print:mt-8">
      <h2 className="font-serif text-xl font-semibold mb-4">参考来源</h2>
      {searchQueries && searchQueries.length > 0 && (
        <div className="mb-6">
          <p className="text-[10px] font-mono uppercase tracking-widest text-silver mb-2">检索关键词</p>
          <div className="flex flex-wrap gap-2">
            {searchQueries.map((q) => (
              <span key={q} className="text-xs font-mono border border-smoke px-2 py-1 text-ash">
                {q}
              </span>
            ))}
          </div>
        </div>
      )}
      {citations.length > 0 && (
        <ol className="space-y-3 list-none">
          {citations.map((c) => (
            <li key={c.id} className="text-sm leading-relaxed">
              <span className="font-mono text-xs text-silver mr-2">[{c.id}]</span>
              <a
                href={c.url}
                target="_blank"
                rel="noopener noreferrer"
                className="font-medium hover:underline underline-offset-2"
              >
                {c.title}
              </a>
              <span className="ml-2 text-[10px] font-mono border border-smoke px-1.5 py-0.5 text-silver">
                {c.source_type === 'article' ? '平台资讯' : '网络检索'}
              </span>
              {c.snippet && (
                <p className="mt-1 text-xs text-ash pl-6 line-clamp-2">{c.snippet}</p>
              )}
            </li>
          ))}
        </ol>
      )}
    </section>
  )
}
