import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { Hotspot, HotspotFilters, HotspotSummary, Source } from '../types'
import HotCard from '../components/HotCard'
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

export default function HotspotPage() {
  const [filters, setFilters] = useState<HotspotFilters>({
    hours: 24,
    sort: 'heat',
    heat_level: '',
    category: '',
    source_id: '',
    only_new: false,
    min_sources: 0,
    q: '',
  })
  const [items, setItems] = useState<Hotspot[]>([])
  const [summary, setSummary] = useState<HotspotSummary | null>(null)
  const [sources, setSources] = useState<Source[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getSources().then(setSources).catch(console.error)
  }, [])

  useEffect(() => {
    setLoading(true)
    Promise.all([
      api.getHotspots(filters),
      api.getHotspotSummary(filters.hours),
    ])
      .then(([res, sum]) => {
        setItems(res.items)
        setTotal(res.total)
        setSummary(sum)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [filters])

  function setFilter<K extends keyof HotspotFilters>(key: K, value: HotspotFilters[K]) {
    setFilters((f) => ({ ...f, [key]: value }))
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-12">
      <header className="mb-8 pb-6 border-b border-ink">
        <p className="text-[10px] font-mono uppercase tracking-widest text-silver mb-2">Hotspot Feed</p>
        <h1 className="font-serif text-3xl font-semibold">咨询汇总</h1>
        <p className="mt-2 text-sm text-ash max-w-2xl">
          多源 AI 资讯聚合，按信噪比动态分层，参考
          {' '}<a href="https://github.com/tbang6860-commits/aihot" target="_blank" rel="noopener noreferrer" className="underline">PulseSphere</a>
          {' '}热点看板设计。
        </p>
      </header>

      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-8">
          <Stat label="总计" value={summary.total} />
          <Stat label="高热" value={summary.heat_tiers.high} />
          <Stat label="中热" value={summary.heat_tiers.medium} />
          <Stat label="24h 新增" value={summary.new_count} />
          <Stat label="数据源" value={Object.keys(summary.by_source).length} />
        </div>
      )}

      <div className="space-y-4 mb-8">
        <div className="flex flex-wrap gap-2">
          {HOURS.map(({ key, label }) => (
            <FilterChip key={key} active={filters.hours === key} onClick={() => setFilter('hours', key)}>{label}</FilterChip>
          ))}
        </div>
        <div className="flex flex-wrap gap-2">
          {SORTS.map(({ key, label }) => (
            <FilterChip key={key} active={filters.sort === key} onClick={() => setFilter('sort', key)}>{label}</FilterChip>
          ))}
        </div>
        <div className="flex flex-wrap gap-2">
          {HEAT_TABS.map(({ key, label }) => (
            <FilterChip key={key || 'all'} active={filters.heat_level === key} onClick={() => setFilter('heat_level', key)}>{label}</FilterChip>
          ))}
          <FilterChip active={filters.only_new} onClick={() => setFilter('only_new', !filters.only_new)}>只看新热点</FilterChip>
          <FilterChip active={filters.min_sources >= 2} onClick={() => setFilter('min_sources', filters.min_sources >= 2 ? 0 : 2)}>跨平台 ≥2源</FilterChip>
        </div>
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map(({ key, label }) => (
            <FilterChip key={key || 'all'} active={filters.category === key} onClick={() => setFilter('category', key)}>{label}</FilterChip>
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
        {loading ? '加载中...' : `共 ${total} 条，当前显示 ${items.length} 条`}
        {summary?.last_updated && ` · 更新 ${new Date(summary.last_updated).toLocaleString('zh-CN')}`}
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
        <EmptyState title="暂无热点" description="调整筛选条件，或点击顶部抓取更新积累数据" />
      )}
    </div>
  )
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="border border-ink p-3">
      <p className="text-[10px] font-mono text-silver">{label}</p>
      <p className="font-serif text-xl font-semibold mt-1">{value}</p>
    </div>
  )
}

function FilterChip({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
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
