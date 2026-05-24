import type { ReportCitation } from '../types'

interface ReportLinkPanelProps {
  links: ReportCitation[]
  compact?: boolean
}

function hostLabel(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch {
    return url.slice(0, 32)
  }
}

export default function ReportLinkPanel({ links, compact = false }: ReportLinkPanelProps) {
  if (!links.length) return null

  const webLinks = links.filter((l) => l.source_type === 'web')
  const articleLinks = links.filter((l) => l.source_type === 'article')

  return (
    <section className={compact ? '' : 'mt-0'}>
      <h2 className="font-serif text-lg font-semibold mb-1">相关链接</h2>
      <p className="text-[10px] font-mono text-silver mb-4">共 {links.length} 条 · 点击跳转原文</p>

      {articleLinks.length > 0 && (
        <LinkGroup title="平台资讯" links={articleLinks} compact={compact} />
      )}
      {webLinks.length > 0 && (
        <LinkGroup title="网络检索" links={webLinks} compact={compact} />
      )}
    </section>
  )
}

function LinkGroup({
  title,
  links,
}: {
  title: string
  links: ReportCitation[]
  compact?: boolean
}) {
  return (
    <div className="mb-5">
      <p className="text-[10px] font-mono uppercase tracking-widest text-silver mb-2">{title}</p>
      <ul className="space-y-2">
        {links.map((link) => (
          <li key={`${link.source_type}-${link.id}-${link.url}`}>
            <a
              href={link.url}
              target="_blank"
              rel="noopener noreferrer"
              className="group block border border-smoke hover:border-ink bg-paper hover:bg-mist px-3 py-2.5 transition-colors"
            >
              <span className="text-sm font-medium leading-snug line-clamp-2 group-hover:underline underline-offset-2">
                {link.title}
              </span>
              <span className="mt-1 flex items-center gap-2 text-[10px] font-mono text-silver">
                <span>{hostLabel(link.url)}</span>
                <span className="opacity-0 group-hover:opacity-100 transition-opacity">↗</span>
              </span>
            </a>
          </li>
        ))}
      </ul>
    </div>
  )
}
