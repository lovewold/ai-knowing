import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import type { DailyBriefing, DailyBriefingItem, Article } from '../types'
import EmptyState from '../components/EmptyState'

function ArticleDetailPanel({ articleId, onClose }: { articleId: number; onClose: () => void }) {
  const [article, setArticle] = useState<Article | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getArticle(articleId).then(setArticle).catch(console.error).finally(() => setLoading(false))
  }, [articleId])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-ink/40" onClick={onClose}>
      <div
        className="bg-paper border border-ink max-w-lg w-full max-h-[80vh] overflow-y-auto p-6 shadow-lg"
        onClick={(e) => e.stopPropagation()}
      >
        {loading ? (
          <p className="text-sm font-mono text-silver">加载中...</p>
        ) : article ? (
          <>
            <h3 className="font-serif text-xl font-semibold leading-snug">{article.title}</h3>
            <div className="mt-3 flex flex-wrap gap-3 text-xs font-mono text-silver">
              <span>{article.source}</span>
              {article.signal_score != null && <span>信号 {Math.round(article.signal_score)}</span>}
            </div>
            {article.summary && (
              <p className="mt-4 text-sm text-ash leading-relaxed">{article.summary}</p>
            )}
            <div className="mt-6 flex gap-3">
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm px-4 py-2 border border-ink hover:bg-ink hover:text-paper transition-colors"
              >
                访问原文 ↗
              </a>
              <button type="button" onClick={onClose} className="text-sm px-4 py-2 border border-smoke text-ash">
                关闭
              </button>
            </div>
          </>
        ) : (
          <p className="text-sm text-ash">无法加载资讯详情</p>
        )}
      </div>
    </div>
  )
}

function BriefingItemRow({
  item,
  index,
  onOpenArticle,
}: {
  item: DailyBriefingItem
  index: number
  onOpenArticle: (id: number) => void
}) {
  const [expanded, setExpanded] = useState(false)

  if (item.item_type === 'creator') {
    return (
      <div className="py-4 border-b border-smoke">
        <div className="flex items-start justify-between gap-4">
          <div>
            <span className="text-[10px] font-mono border border-ink px-1.5 py-0.5 mr-2">抖音</span>
            <a
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium hover:underline underline-offset-2"
            >
              {item.title}
            </a>
            {item.creator_focus && (
              <p className="text-xs text-silver mt-1 font-mono">{item.creator_focus}</p>
            )}
            {item.summary && <p className="text-sm text-ash mt-2 leading-relaxed">{item.summary}</p>}
          </div>
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs font-mono shrink-0 underline text-silver hover:text-ink"
          >
            主页 ↗
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="py-4 border-b border-smoke">
      <button
        type="button"
        className="w-full text-left group"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start gap-4">
          <span className="font-mono text-xs text-silver w-6 shrink-0 pt-0.5">{index + 1}</span>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium leading-relaxed group-hover:underline underline-offset-2">
              {item.title}
            </p>
            {!expanded && item.summary && (
              <p className="text-xs text-ash mt-1.5 line-clamp-2">{item.summary}</p>
            )}
            <div className="flex items-center gap-2 mt-2 text-[10px] font-mono text-silver">
              <span>{item.source_name}</span>
              {item.signal_score != null && <span>{Math.round(item.signal_score)}</span>}
              <span className="text-ash">{expanded ? '收起' : '展开摘要'}</span>
            </div>
          </div>
        </div>
      </button>
      {expanded && (
        <div className="ml-10 mt-3 pl-4 border-l-2 border-ink">
          {item.summary && <p className="text-sm text-ash leading-relaxed">{item.summary}</p>}
          <div className="mt-3 flex flex-wrap gap-2">
            {item.article_id && (
              <button
                type="button"
                onClick={() => onOpenArticle(item.article_id!)}
                className="text-xs font-mono px-3 py-1.5 border border-ink hover:bg-mist"
              >
                查看详情
              </button>
            )}
            <a
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-mono px-3 py-1.5 border border-ink hover:bg-ink hover:text-paper"
            >
              访问原文 ↗
            </a>
          </div>
        </div>
      )}
    </div>
  )
}

export default function DailyBriefingPage() {
  const { id } = useParams()
  const [briefing, setBriefing] = useState<DailyBriefing | null>(null)
  const [history, setHistory] = useState<DailyBriefing[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [detailArticleId, setDetailArticleId] = useState<number | null>(null)

  useEffect(() => {
    setLoading(true)
    const load = id
      ? api.getDailyBriefing(Number(id))
      : api.getLatestDailyBriefing()
    Promise.all([load, api.getDailyBriefings()])
      .then(([b, h]) => { setBriefing(b); setHistory(h) })
      .catch(() => setBriefing(null))
      .finally(() => setLoading(false))
  }, [id])

  async function handleGenerate() {
    setGenerating(true)
    try {
      const b = await api.generateDailyBriefing()
      setBriefing(b)
      const h = await api.getDailyBriefings()
      setHistory(h)
    } catch {
      alert('生成失败，请检查后端与 DeepSeek API')
    } finally {
      setGenerating(false)
    }
  }

  const articleItems = briefing?.items?.filter((i) => i.item_type === 'article') ?? []
  const creatorItems = briefing?.items?.filter((i) => i.item_type === 'creator') ?? []

  return (
    <div className="max-w-3xl mx-auto px-6 py-12">
      <header className="mb-8 pb-6 border-b border-ink">
        <h1 className="font-serif text-3xl font-semibold">每日晨报</h1>
        <p className="mt-2 text-sm text-ash">24 小时高信号资讯汇总</p>
        <button
          type="button"
          onClick={handleGenerate}
          disabled={generating}
          className="mt-4 line-border px-4 py-2 text-sm font-medium hover:bg-ink hover:text-paper disabled:opacity-40"
        >
          {generating ? '生成中...' : '生成今日晨报'}
        </button>
      </header>

      {history.length > 1 && (
        <div className="mb-8 flex flex-wrap gap-2">
          {history.map((h) => (
            <Link
              key={h.id}
              to={h.id === briefing?.id ? '/briefing' : `/briefing/${h.id}`}
              className={`text-xs font-mono px-3 py-1 border ${
                briefing?.id === h.id ? 'bg-ink text-paper border-ink' : 'border-smoke text-ash hover:border-ink'
              }`}
            >
              {h.briefing_date}
            </Link>
          ))}
        </div>
      )}

      {loading ? (
        <p className="text-sm font-mono text-silver">加载中...</p>
      ) : !briefing ? (
        <EmptyState
          title="暂无晨报"
          description="请先触发抓取积累高信号资讯，再点击生成今日晨报"
        />
      ) : (
        <article>
          <div className="mb-10 p-6 border border-ink bg-mist/40">
            <h2 className="font-serif text-xl font-semibold mb-3">{briefing.title}</h2>
            {briefing.theme_tags && (
              <div className="flex flex-wrap gap-2 mb-4">
                {briefing.theme_tags.split(/[,，]/).map((tag) => (
                  <span key={tag.trim()} className="text-[10px] font-mono border border-ink px-2 py-0.5">
                    {tag.trim()}
                  </span>
                ))}
              </div>
            )}
            <p className="text-sm text-ash leading-[1.85] whitespace-pre-line">{briefing.overview}</p>
            <p className="mt-4 text-xs font-mono text-silver">
              {briefing.article_count} 条高质量资讯 · {new Date(briefing.created_at).toLocaleString('zh-CN')}
            </p>
          </div>

          <section className="mb-12">
            <h3 className="font-serif text-lg font-semibold mb-4 pb-2 border-b border-ink">
              高质量资讯
            </h3>
            {articleItems.length ? (
              articleItems.map((item, i) => (
                <BriefingItemRow
                  key={item.id}
                  item={item}
                  index={i}
                  onOpenArticle={setDetailArticleId}
                />
              ))
            ) : (
              <p className="text-sm text-silver">今日暂无达到质量阈值的资讯</p>
            )}
          </section>

          {creatorItems.length > 0 && (
            <section>
              <h3 className="font-serif text-lg font-semibold mb-2 pb-2 border-b border-ink">
                抖音博主推荐
              </h3>
              <p className="text-xs text-silver mb-4">
                人工 curated 优质 AI 创作者，可在 config/douyin_creators.yaml 增删
              </p>
              {creatorItems.map((item, i) => (
                <BriefingItemRow key={item.id} item={item} index={i} onOpenArticle={setDetailArticleId} />
              ))}
            </section>
          )}
        </article>
      )}

      {detailArticleId != null && (
        <ArticleDetailPanel articleId={detailArticleId} onClose={() => setDetailArticleId(null)} />
      )}
    </div>
  )
}
