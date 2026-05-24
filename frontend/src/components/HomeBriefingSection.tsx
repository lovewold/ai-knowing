import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import type { DailyBriefing, DailyBriefingItem } from '../types'

function BriefingNewsItem({ item }: { item: DailyBriefingItem }) {
  return (
    <a
      href={item.url}
      target="_blank"
      rel="noopener noreferrer"
      className="group block border border-smoke hover:border-ink p-4 bg-paper hover:bg-mist transition-colors h-full"
    >
      <p className="text-sm font-medium leading-snug line-clamp-2 group-hover:underline underline-offset-2">
        {item.title}
      </p>
      {item.summary && (
        <p className="mt-2 text-xs text-ash leading-relaxed line-clamp-4">{item.summary}</p>
      )}
      <div className="mt-3 flex items-center gap-2 text-[10px] font-mono text-silver">
        <span>{item.source_name}</span>
        {item.signal_score != null && <span>{Math.round(item.signal_score)} 分</span>}
      </div>
    </a>
  )
}

export default function HomeBriefingSection() {
  const [briefing, setBriefing] = useState<DailyBriefing | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    api.getLatestDailyBriefing()
      .then(setBriefing)
      .catch(() => setBriefing(null))
      .finally(() => setLoading(false))
  }, [])

  async function handleGenerate() {
    setGenerating(true)
    try {
      setBriefing(await api.generateDailyBriefing())
    } catch {
      alert('晨报生成失败')
    } finally {
      setGenerating(false)
    }
  }

  const articleItems = briefing?.items?.filter((i) => i.item_type === 'article') ?? []

  return (
    <section className="border-b border-ink bg-mist/30">
      <div className="max-w-6xl mx-auto px-6 py-12">
        <div className="flex flex-wrap items-end justify-between gap-4 mb-8">
          <div>
            <p className="text-[10px] font-mono uppercase tracking-widest text-silver mb-1">每日晨报</p>
            <h2 className="font-serif text-2xl font-semibold">今日 AI 要闻</h2>
          </div>
          <button
            type="button"
            onClick={handleGenerate}
            disabled={generating}
            className="line-border px-4 py-2 text-sm font-medium hover:bg-ink hover:text-paper disabled:opacity-40"
          >
            {generating ? '生成中…' : '刷新晨报'}
          </button>
        </div>

        {loading ? (
          <p className="text-sm font-mono text-silver">加载中...</p>
        ) : !briefing ? (
          <div className="border border-ink bg-paper p-8 text-center">
            <p className="text-sm text-ash mb-4">暂无晨报，抓取资讯后点击刷新生成</p>
            <button type="button" onClick={handleGenerate} disabled={generating} className="text-sm underline">
              生成今日晨报
            </button>
          </div>
        ) : (
          <>
            <article className="border border-ink bg-paper p-6 md:p-8 mb-8">
              <h3 className="font-serif text-xl font-semibold mb-3">{briefing.title}</h3>
              {briefing.theme_tags && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {briefing.theme_tags.split(/[,，]/).filter(Boolean).map((tag) => (
                    <span key={tag.trim()} className="text-[10px] font-mono border border-ink px-2 py-0.5">
                      {tag.trim()}
                    </span>
                  ))}
                </div>
              )}
              <div className="text-sm md:text-base text-ash leading-[1.95] whitespace-pre-line">{briefing.overview}</div>
              <p className="mt-5 text-xs font-mono text-silver">
                {briefing.article_count} 条资讯 · {new Date(briefing.created_at).toLocaleString('zh-CN')}
              </p>
            </article>

            {articleItems.length > 0 && (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-serif text-lg font-semibold">AI 新闻精选</h3>
                  <Link to="/news" className="text-xs font-mono text-ash hover:text-ink underline">
                    查看全部
                  </Link>
                </div>
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {articleItems.slice(0, 9).map((item) => (
                    <BriefingNewsItem key={item.id} item={item} />
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </section>
  )
}
