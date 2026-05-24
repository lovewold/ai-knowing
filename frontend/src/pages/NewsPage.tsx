import { useEffect, useState, type ReactNode } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api } from '../api/client'
import type { Article, Hotspot, HotspotFilters, HotspotSummary, Source } from '../types'
import HotCard from '../components/HotCard'
import ArticleRow from '../components/ArticleRow'
import EmptyState from '../components/EmptyState'

const SORTS = [
  { key: 'heat', label: '最热' },
  { key: 'newest', label: '最新' },
  { key: 'cross_source', label: '跨平台' },
] as const

const HEAT_TABS = [
  { key: '', label: '全部' },
  { key: 'high', label: '高热' },
  { key: 'medium', label: '中热' },
  { key: 'low', label: '低热' },
] as const

const SIGNAL_TABS = [
  { key: '', label: '全部信号' },
  { key: 'high', label: '高信号' },
  { key: 'medium', label: '观察' },
  { key: 'low', label: '低信号' },
] as const

const HOURS = [
  { key: 24, label: '24h' },
  { key: 72, label: '72h' },
  { key: 168, label: '7d' },
] as const

const CATEGORIES = [
  { key: '', label: '全部' },
  { key: 'news', label: '资讯' },
  { key: 'agent', label: 'Agent' },
  { key: 'tool', label: '工具' },
  { key: 'paper', label: '论文' },
] as const

export default function NewsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const view = searchParams.get('view') === 'list' ? 'list' : 'hotspot'

  const [filters, setFilters] = useState<HotspotFilters>({
    hours: 24,
    sort: 'heat',
    heat_level: '',
    signal_status: '',
    category: '',
    source_id: '',
    only_new: false,
    min_sources: 0,
    q: '',
  })
  const [items, setItems] = useState<Hotspot[]>([])
  const [articles, setArticles] = useState<Article[]>([])
  const [summary, setSummary] = useState<HotspotSummary | null>(null)
  const [sources, setSources] = useState<Source[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getSources().then(setSources).catch(console.error)
  }, [])

  useEffect(() => {
    if (view === 'list') {
      setLoading(true)
      api.getArticles(undefined, 60)
        .then(setArticles)
        .catch(console.error)
        .finally(() => setLoading(false))
      return
    }
    setLoading(true)
    Promise.all([api.getHotspots(filters), api.getHotspotSummary(filters.hours)])
      .then(([res, sum]) => {
        setItems(res.items)
        setTotal(res.total)
        setSummary(sum)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [view, filters])

  function setFilter<K extends keyof HotspotFilters>(key: K, value: HotspotFilters[K]) {
    setFilters((f) => ({ ...f, [key]: value }))
  }

  function switchView(next: 'hotspot' | 'list') {
    if (next === 'list') {
      setSearchParams({ view: 'list' })
    } else {
      setSearchParams({})
    }
  }

  const highCount = articles.filter((a) => a.signal_status === 'high').length

  return (
    <div className="max-w-6xl mx-auto px-6 py-12">
      <header className="mb-8 pb-6 border-b border-ink">
        <h1 className="font-serif text-3xl font-semibold">AI 资讯</h1>
        <p className="mt-2 text-sm text-ash">多源 AI 资讯聚合，按信噪比动态分层</p>
        <div className="mt-6 flex gap-2">
          <ViewTab active={view === 'hotspot'} onClick={() => switchView('hotspot')}>热点看板</ViewTab>
          <ViewTab active={view === 'list'} onClick={() => switchView('list')}>资讯列表</ViewTab>
        </div>
      </header>

      {view === 'list' ? (
        <>
          <p className="text-xs font-mono text-silver mb-6">按信噪比分排序 · 高信号 {highCount} 条</p>
          {loading ? <p className="text-sm text-silver font-mono">加载中...</p>
            : articles.length ? articles.map((a, i) => <ArticleRow key={a.id} article={a} index={i} />)
            : <EmptyState title="暂无资讯" description="点击抓取更新" />}
        </>
      ) : (
        <>
          {summary && (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-8">
              <Stat label="总计" value={summary.total} />
              <Stat label="高信号" value={summary.signal_tiers?.high ?? 0} accent />
              <Stat label="观察" value={summary.signal_tiers?.medium ?? 0} />
              <Stat label="高热" value={summary.heat_tiers.high} />
              <Stat label="24h 新增" value={summary.new_count} />
              <Stat label="数据源" value={Object.keys(summary.by_source).length} />
            </div>
          )}

          <div className="space-y-3 mb-8">
            <div className="flex flex-wrap gap-2">
              {HOURS.map(({ key, label }) => (
                <FilterChip key={key} active={filters.hours === key} onClick={() => setFilter('hours', key)}>{label}</FilterChip>
              ))}
              {SORTS.map(({ key, label }) => (
                <FilterChip key={key} active={filters.sort === key} onClick={() => setFilter('sort', key)}>{label}</FilterChip>
              ))}
            </div>
            <div className="flex flex-wrap gap-2">
              {SIGNAL_TABS.map(({ key, label }) => (
                <FilterChip key={key || 'sig-all'} active={filters.signal_status === key} onClick={() => setFilter('signal_status', key)}>{label}</FilterChip>
              ))}
            </div>
            <div className="flex flex-wrap gap-2">
              {HEAT_TABS.map(({ key, label }) => (
                <FilterChip key={key || 'heat-all'} active={filters.heat_level === key} onClick={() => setFilter('heat_level', key)}>{label}</FilterChip>
              ))}
              <FilterChip active={filters.only_new} onClick={() => setFilter('only_new', !filters.only_new)}>只看新热点</FilterChip>
              <FilterChip active={filters.min_sources >= 2} onClick={() => setFilter('min_sources', filters.min_sources >= 2 ? 0 : 2)}>跨平台 ≥2源</FilterChip>
            </div>
            <div className="flex flex-wrap gap-2">
              {CATEGORIES.map(({ key, label }) => (
                <FilterChip key={key || 'cat-all'} active={filters.category === key} onClick={() => setFilter('category', key)}>{label}</FilterChip>
              ))}
            </div>
            <div className="flex flex-wrap gap-2 items-center">
              <select
                className="border border-smoke px-2 py-1.5 text-xs font-mono bg-paper"
                value={filters.source_id}
                onChange={(e) => setFilter('source_id', e.target.value)}
              >
                <option value="">全部来源</option>
                {sources.map((s) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
              <input
                type="search"
                placeholder="搜索标题或摘要..."
                className="border border-smoke px-3 py-1.5 text-sm flex-1 min-w-[200px] max-w-md"
                value={filters.q}
                onChange={(e) => setFilter('q', e.target.value)}
              />
            </div>
          </div>

          <p className="text-xs font-mono text-silver mb-4">
            {loading ? '加载中...' : `共 ${total} 条`}
            {summary?.last_updated && ` · ${new Date(summary.last_updated).toLocaleString('zh-CN')}`}
          </p>

          {loading ? (
            <p className="text-sm text-silver font-mono">加载中...</p>
          ) : items.length ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 border-t border-ink pt-6">
              {items.map((h, i) => (
                <HotCard key={h.id} hotspot={h} rank={filters.sort === 'heat' ? i + 1 : undefined} />
              ))}
            </div>
          ) : (
            <EmptyState title="暂无热点" description="调整筛选条件或抓取更新" />
          )}
        </>
      )}
    </div>
  )
}

function Stat({ label, value, accent }: { label: string; value: number; accent?: boolean }) {
  return (
    <div className={`border border-ink p-3 ${accent ? 'bg-mist' : 'bg-paper'}`}>
      <p className="text-[10px] font-mono text-silver">{label}</p>
      <p className="font-serif text-xl font-semibold mt-1">{value}</p>
    </div>
  )
}

function FilterChip({ active, onClick, children }: { active: boolean; onClick: () => void; children: ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`px-3 py-1.5 text-xs font-medium border border-ink ${active ? 'bg-ink text-paper' : 'hover:bg-mist text-ash'}`}
    >
      {children}
    </button>
  )
}

function ViewTab({ active, onClick, children }: { active: boolean; onClick: () => void; children: ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`px-4 py-2 text-sm font-medium border border-ink ${active ? 'bg-ink text-paper' : 'text-ash hover:bg-mist'}`}
    >
      {children}
    </button>
  )
}
