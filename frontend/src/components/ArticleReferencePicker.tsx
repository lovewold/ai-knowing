import { useEffect, useMemo, useState } from 'react'
import { api } from '../api/client'
import type { Article } from '../types'
import SignalBadge from './SignalBadge'

const MAX_SELECT = 10

interface ArticleReferencePickerProps {
  selectedIds: number[]
  onChange: (ids: number[]) => void
  disabled?: boolean
}

export default function ArticleReferencePicker({
  selectedIds,
  onChange,
  disabled = false,
}: ArticleReferencePickerProps) {
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')

  useEffect(() => {
    api.getArticles(undefined, 45)
      .then(setArticles)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return articles
    return articles.filter((a) => {
      const text = [a.title, a.summary, a.source].filter(Boolean).join(' ').toLowerCase()
      return text.includes(q)
    })
  }, [articles, query])

  function toggle(id: number) {
    if (disabled) return
    if (selectedIds.includes(id)) {
      onChange(selectedIds.filter((x) => x !== id))
      return
    }
    if (selectedIds.length >= MAX_SELECT) return
    onChange([...selectedIds, id])
  }

  function clearAll() {
    if (!disabled) onChange([])
  }

  return (
    <section className="border-t border-ink pt-6 mt-2">
      <div className="flex flex-wrap items-end justify-between gap-3 mb-4">
        <div>
          <h3 className="font-serif text-base font-semibold">{'\u5f15\u7528\u8d44\u8baf'}</h3>
          <p className="mt-1 text-xs text-ash">
            {'\u52fe\u9009\u5e76\u52a0\u5165\u62a5\u544a\u5f15\u7528\uff0c\u6700\u591a '}{MAX_SELECT}{'\u6761'}
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs font-mono">
          <span className="text-silver">
            {'\u5df2\u9009 '}{selectedIds.length}{' / '}{MAX_SELECT}
          </span>
          {selectedIds.length > 0 && (
            <button
              type="button"
              onClick={clearAll}
              disabled={disabled}
              className="underline text-ash hover:text-ink disabled:opacity-40"
            >
              {'\u6e05\u7a7a'}
            </button>
          )}
        </div>
      </div>

      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={'\u641c\u7d22\u6807\u9898\u6216\u6458\u8981...'}
        disabled={disabled || loading}
        className="w-full border border-smoke px-3 py-2 text-sm mb-3 bg-paper focus:outline-none focus:ring-1 focus:ring-ink"
      />

      {loading ? (
        <p className="text-sm text-silver font-mono">{'\u52a0\u8f7d\u4e2d...'}</p>
      ) : filtered.length === 0 ? (
        <p className="text-sm text-silver">{'\u6682\u65e0\u53ef\u9009\u8d44\u8baf'}</p>
      ) : (
        <ul className="max-h-72 overflow-y-auto border border-ink divide-y divide-smoke">
          {filtered.map((article) => {
            const checked = selectedIds.includes(article.id)
            const atMax = !checked && selectedIds.length >= MAX_SELECT
            return (
              <li key={article.id}>
                <label
                  className={`flex items-start gap-3 px-3 py-3 cursor-pointer transition-colors ${
                    checked ? 'bg-mist' : 'hover:bg-mist/60'
                  } ${atMax || disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <input
                    type="checkbox"
                    checked={checked}
                    disabled={disabled || atMax}
                    onChange={() => toggle(article.id)}
                    className="mt-1 accent-ink shrink-0"
                  />
                  <span className="min-w-0 flex-1">
                    <span className="flex items-start justify-between gap-2">
                      <span className="text-sm font-medium leading-snug line-clamp-2">{article.title}</span>
                      <SignalBadge status={article.signal_status} score={article.signal_score} />
                    </span>
                    <span className="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-[10px] font-mono text-silver">
                      <span>{article.source}</span>
                      {checked && (
                        <span className="border border-ink px-1 py-0.5 text-ink">
                          {'\u5f15\u7528 ['}{selectedIds.indexOf(article.id) + 1}{']'}
                        </span>
                      )}
                    </span>
                    {article.summary && (
                      <p className="mt-1 text-xs text-ash line-clamp-2 leading-relaxed">{article.summary}</p>
                    )}
                  </span>
                </label>
              </li>
            )
          })}
        </ul>
      )}
    </section>
  )
}
