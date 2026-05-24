from pathlib import Path

HOTSPOT_PAGE = r'''import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { Hotspot, HotspotFilters, HotspotSummary, Source } from '../types'
import HotCard from '../components/HotCard'
import EmptyState from '../components/EmptyState'

const SORTS = [
  { key: 'heat', label: '\u6700\u70ed' },
  { key: 'newest', label: '\u6700\u65b0' },
  { key: 'cross_source', label: '\u8de8\u5e73\u53f0' },
] as const

const HEAT_TABS = [
  { key: '', label: '\u5168\u90e8' },
  { key: 'high', label: '\u9ad8\u70ed' },
  { key: 'medium', label: '\u4e2d\u70ed' },
  { key: 'low', label: '\u4f4e\u70ed' },
] as const

const HOURS = [
  { key: 24, label: '24h' },
  { key: 72, label: '72h' },
  { key: 168, label: '7d' },
] as const

const CATEGORIES = [
  { key: '', label: '\u5168\u90e8' },
  { key: 'news', label: '\u8d44\u8baf' },
  { key: 'agent', label: 'Agent' },
  { key: 'tool', label: '\u5de5\u5177' },
  { key: 'paper', label: '\u8bba\u6587' },
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
        <h1 className="font-serif text-3xl font-semibold">\u54a8\u8be2\u6c47\u603b</h1>
        <p className="mt-2 text-sm text-ash max-w-2xl">
          \u591a\u6e90 AI \u8d44\u8baf\u805a\u5408\uff0c\u6309\u4fe1\u566a\u6bd4\u52a8\u6001\u5206\u5c42\uff0c\u53c2\u8003
          {' '}<a href="https://github.com/tbang6860-commits/aihot" target="_blank" rel="noopener noreferrer" className="underline">PulseSphere</a>
          {' '}\u70ed\u70b9\u770b\u677f\u8bbe\u8ba1\u3002
        </p>
      </header>

      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-8">
          <Stat label="\u603b\u8ba1" value={summary.total} />
          <Stat label="\u9ad8\u70ed" value={summary.heat_tiers.high} />
          <Stat label="\u4e2d\u70ed" value={summary.heat_tiers.medium} />
          <Stat label="24h \u65b0\u589e" value={summary.new_count} />
          <Stat label="\u6570\u636e\u6e90" value={Object.keys(summary.by_source).length} />
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
          <FilterChip active={filters.only_new} onClick={() => setFilter('only_new', !filters.only_new)}>\u53ea\u770b\u65b0\u70ed\u70b9</FilterChip>
          <FilterChip active={filters.min_sources >= 2} onClick={() => setFilter('min_sources', filters.min_sources >= 2 ? 0 : 2)}>\u8de8\u5e73\u53f0 \u22652\u6e90</FilterChip>
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
            <option value="">\u5168\u90e8\u6765\u6e90</option>
            {sources.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
          <input
            type="search"
            placeholder="\u641c\u7d22\u6807\u9898\u6216\u6458\u8981..."
            className="border border-smoke px-3 py-1.5 text-sm flex-1 min-w-[200px] max-w-md"
            value={filters.q}
            onChange={(e) => setFilter('q', e.target.value)}
          />
        </div>
      </div>

      <p className="text-xs font-mono text-silver mb-4">
        {loading ? '\u52a0\u8f7d\u4e2d...' : `\u5171 ${total} \u6761\uff0c\u5f53\u524d\u663e\u793a ${items.length} \u6761`}
        {summary?.last_updated && ` \u00b7 \u66f4\u65b0 ${new Date(summary.last_updated).toLocaleString('zh-CN')}`}
      </p>

      {loading ? (
        <p className="text-sm text-silver font-mono">\u52a0\u8f7d\u4e2d...</p>
      ) : items.length ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 border-t border-ink pt-6">
          {items.map((h, i) => (
            <HotCard key={h.id} hotspot={h} rank={filters.sort === 'heat' ? i + 1 : undefined} />
          ))}
        </div>
      ) : (
        <EmptyState title="\u6682\u65e0\u70ed\u70b9" description="\u8c03\u6574\u7b5b\u9009\u6761\u4ef6\uff0c\u6216\u70b9\u51fb\u9876\u90e8\u6293\u53d6\u66f4\u65b0\u79ef\u7d2f\u6570\u636e" />
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
'''

def decode(s: str) -> str:
    return s.encode('utf-8').decode('unicode_escape')

Path(r'c:\Users\user\Desktop\ai-know(1)\frontend\src\pages\HotspotPage.tsx').write_text(decode(HOTSPOT_PAGE), encoding='utf-8')
print('wrote HotspotPage.tsx')
