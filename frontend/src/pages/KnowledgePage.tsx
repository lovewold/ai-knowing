import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../api/client'
import type { KnowledgeEntry, ProductCatalogGroup } from '../types'
import EmptyState from '../components/EmptyState'

const TABS = [
  { key: '', label: '\u5168\u90e8' },
  { key: 'model', label: '\u6a21\u578b' },
  { key: 'product', label: '\u4ea7\u54c1' },
  { key: 'skill', label: 'Skill/\u5de5\u5177' },
]

function StaleBadge({ stale }: { stale?: boolean }) {
  if (!stale) return null
  return <span className="text-[10px] font-mono border border-amber-600 text-amber-800 px-1.5 py-0.5 ml-2">{'\u8d85 30 \u5929\u672a\u9a8c\u8bc1'}</span>
}

export default function KnowledgePage() {
  const [params, setParams] = useSearchParams()
  const kind = params.get('kind') || ''
  const category = params.get('category') || ''
  const [items, setItems] = useState<KnowledgeEntry[]>([])
  const [catalog, setCatalog] = useState<ProductCatalogGroup[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getProductCatalog().then((r) => setCatalog(r.groups)).catch(() => setCatalog([]))
  }, [])

  useEffect(() => {
    setLoading(true)
    api.getKnowledgeList(kind || undefined, undefined, category || undefined).then(setItems).catch(console.error).finally(() => setLoading(false))
  }, [kind, category])

  const productCategories = catalog.map((g) => g.category)

  function setKindTab(key: string) {
    if (key) setParams({ kind: key })
    else setParams({})
  }

  function setCategoryTab(cat: string) {
    const p: Record<string, string> = { category: cat }
    p.kind = kind || 'product'
    setParams(p)
  }

  function clearCategory() {
    if (kind) setParams({ kind })
    else setParams({})
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <header className="mb-8 pb-6 border-b border-ink">
        <h1 className="text-3xl font-semibold">{'\u77e5\u8bc6\u5e93'}</h1>
        <p className="mt-2 text-sm text-ash leading-relaxed max-w-2xl">
          {'\u6a21\u578b\u80fd\u529b\u3001AI \u4ea7\u54c1\u4e0e Skill \u6559\u7a0b\u6c47\u603b\uff0c\u652f\u6301\u5411\u91cf\u68c0\u7d22\u3001AI \u95ee\u7b54\u4e0e\u62a5\u544a\u751f\u6210\u3002'}
        </p>
        <p className="mt-2 text-xs font-mono text-silver">
          {'\u4ea7\u54c1\u6e05\u5355\u5171 '}{catalog.reduce((n, g) => n + g.count, 0)}{'\u6761\uff0c\u6309\u7c7b\u578b\u5206\u7ec4\u3002\u7f3a\u5c11\u6587\u6863\u53ef\u5728\u7ba1\u7406\u540e\u53f0\u4f7f\u7528 AI \u6279\u91cf\u751f\u6210\u3002'}
        </p>
      </header>
      <div className="flex flex-wrap gap-2 mb-4">
        {TABS.map(({ key, label }) => (
          <button
            key={key || 'all'}
            type="button"
            onClick={() => setKindTab(key)}
            className={`px-4 py-2 text-sm font-medium border border-ink ${kind === key ? 'bg-ink text-paper' : 'hover:bg-mist text-ash'}`}
          >
            {label}
          </button>
        ))}
      </div>
      {(kind === 'product' || !kind) && productCategories.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-8">
          <button type="button" onClick={clearCategory} className={`px-3 py-1 text-xs border ${!category ? 'border-ink bg-mist' : 'border-smoke'}`}>{'\u5168\u90e8\u5206\u7c7b'}</button>
          {productCategories.map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => setCategoryTab(cat)}
              className={`px-3 py-1 text-xs border ${category === cat ? 'border-ink bg-mist' : 'border-smoke hover:border-ink'}`}
            >
              {cat}
            </button>
          ))}
        </div>
      )}
      {loading ? <p className="text-sm text-silver font-mono">{'\u52a0\u8f7d\u4e2d...'}</p>
        : items.length ? (
          <div className="grid sm:grid-cols-2 gap-4">
            {items.map((item) => (
              <Link key={item.id} to={`/knowledge/${item.id}`} className="block border border-smoke hover:border-ink p-5 bg-paper hover:bg-mist transition-colors">
                <div className="flex items-start justify-between gap-2">
                  <span className="text-[10px] font-mono uppercase text-silver">{item.kind}{item.tags ? ` \u00b7 ${item.tags.split(',')[0]}` : ''}</span>
                  <StaleBadge stale={item.stale} />
                </div>
                <h2 className="text-lg font-semibold mt-2 leading-snug">{item.name}</h2>
                {item.summary && <p className="text-sm text-ash mt-2 line-clamp-3 leading-relaxed">{item.summary}</p>}
                {!item.content_md && <p className="text-[10px] font-mono text-amber-800 mt-2">{'\u5f85\u751f\u6210\u6587\u6863'}</p>}
                {item.last_verified_at && (
                  <p className="text-[10px] font-mono text-silver mt-3">
                    {'\u9a8c\u8bc1\u4e8e '}{new Date(item.last_verified_at).toLocaleDateString('zh-CN')}
                  </p>
                )}
              </Link>
            ))}
          </div>
        ) : <EmptyState title={'\u6682\u65e0\u6761\u76ee'} description={'\u7ba1\u7406\u540e\u53f0\u8fd0\u884c\u79cd\u5b50\u6216 AI \u751f\u6210\u6587\u6863'} />}
    </div>
  )
}
