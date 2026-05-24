import { useEffect, useMemo, useState } from 'react'
import { api } from '../api/client'
import type { Article } from '../types'
import SignalBadge from './SignalBadge'

const MAX_SELECT = 12

interface ArticleDiscussPickerProps {
  selectedIds: number[]
  onChange: (ids: number[]) => void
  disabled?: boolean
}

export default function ArticleDiscussPicker({
  selectedIds,
  onChange,
  disabled = false,
}: ArticleDiscussPickerProps) {
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

  const selectedArticles = useMemo(
    () => selectedIds.map((id) => articles.find((a) => a.id === id)).filter(Boolean) as Article[],
    [selectedIds, articles],
  )

  function toggle(id: number) {
    if (disabled) return
    if (selectedIds.includes(id)) {
      onChange(selectedIds.filter((x) => x !== id))
      return
    }
    if (selectedIds.length >= MAX_SELECT) return
    onChange([...selectedIds, id])
  }

  function selectAllVisible() {
    if (disabled) return
    const ids = filtered.map((a) => a.id)
    const merged = [...selectedIds]
    for (const id of ids) {
      if (merged.length >= MAX_SELECT) break
      if (!merged.includes(id)) merged.push(id)
    }
    onChange(merged)
  }

  function clearAll() {
    if (!disabled) onChange([])
  }

  return (
    <section className="border-t border-ink bg-mist/30 px-6 py-6">
      <div className="flex flex-wrap items-end justify-between gap-3 mb-4">
        <div>
          <h3 className="font-serif text-base font-semibold">讨论资讯</h3>
          <p className="mt-1 text-xs text-ash">
            勾选 AI 资讯作为报告讨论素材，生成时纳入分析上下文（最多 {MAX_SELECT} 条）
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="text-silver">已选 {selectedIds.length} / {MAX_SELECT}</span>
          <button
            type="button"
            onClick={selectAllVisible}
            disabled={disabled || loading || filtered.length === 0}
            className="px-2 py-1 border border-smoke hover:border-ink disabled:opacity-40"
          >
            全选当前
          </button>
          {selectedIds.length > 0 && (
            <button
              type="button"
              onClick={clearAll}
              disabled={disabled}
              className="underline text-ash hover:text-ink disabled:opacity-40"
            >
              清空
            </button>
          )}
        </div>
      </div>

      {selectedArticles.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {selectedArticles.map((a) => (
            <button
              key={a.id}
              type="button"
              disabled={disabled}
              onClick={() => toggle(a.id)}
              className="text-xs px-2 py-1 border border-ink bg-paper hover:bg-mist max-w-[240px] truncate"
              title={a.title}
            >
              {a.title.length > 28 ? `${a.title.slice(0, 28)}…` : a.title} ×
            </button>
          ))}
        </div>
      )}

      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="搜索标题或摘要..."
        disabled={disabled || loading}
        className="w-full border border-smoke px-3 py-2 text-sm mb-3 bg-paper focus:outline-none focus:ring-1 focus:ring-ink"
      />

      {loading ? (
        <p className="text-sm text-silver font-mono">加载中...</p>
      ) : filtered.length === 0 ? (
        <p className="text-sm text-silver">暂无可选资讯</p>
      ) : (
        <ul className="max-h-80 overflow-y-auto border border-ink divide-y divide-smoke bg-paper">
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
                    <span className="mt-1 text-[10px] font-mono text-silver">{article.source}</span>
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
