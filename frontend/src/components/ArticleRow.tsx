import type { Article } from '../types'
import SignalBadge from './SignalBadge'

interface ArticleRowProps {
  article: Article
  index?: number
}

export default function ArticleRow({ article, index = 0 }: ArticleRowProps) {
  const date = new Date(article.fetched_at).toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
  })

  return (
    <a
      href={article.url}
      target="_blank"
      rel="noopener noreferrer"
      className={`group block border-b border-smoke py-4 animate-slide-up opacity-0 stagger-${Math.min(index + 1, 5)} hover:bg-mist transition-colors`}
    >
      <div className="flex items-start gap-4">
        <span className="font-mono text-xs text-silver w-12 shrink-0 pt-0.5">{date}</span>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium leading-relaxed group-hover:underline underline-offset-2">
            {article.title}
          </p>
          {article.summary && (
            <p className="text-xs text-ash mt-1.5 leading-relaxed line-clamp-2">{article.summary}</p>
          )}
          <div className="flex items-center gap-3 mt-2">
            <span className="text-[10px] font-mono text-silver uppercase tracking-wider">{article.source}</span>
            {article.category && article.category !== 'news' && (
              <span className="text-[10px] font-mono border border-ink px-1.5 py-0.5">{article.category}</span>
            )}
            <SignalBadge status={article.signal_status} score={article.signal_score} />
          </div>
        </div>
        <span className="text-silver text-xs opacity-0 group-hover:opacity-100 shrink-0 pt-1">{'↗'}</span>
      </div>
    </a>
  )
}
