import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../api/client'
import type { ModelCatalogItem, ModelMarketMeta } from '../types'
import EmptyState from '../components/EmptyState'

export default function ModelMarketPage() {
  const [params, setParams] = useSearchParams()
  const provider = params.get('provider') || ''
  const scene = params.get('scene') || ''
  const q = params.get('q') || ''
  const free = params.get('free') || ''
  const [meta, setMeta] = useState<ModelMarketMeta | null>(null)
  const [items, setItems] = useState<ModelCatalogItem[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [searchInput, setSearchInput] = useState(q)

  useEffect(() => {
    api.getModelMarketMeta().then(setMeta).catch(console.error)
  }, [])

  useEffect(() => {
    setLoading(true)
    api
      .getModelMarketList({
        provider: provider || undefined,
        scene: scene || undefined,
        q: q || undefined,
        free: free === '1' ? true : free === '0' ? false : undefined,
        limit: 80,
      })
      .then((res) => {
        setItems(res.items)
        setTotal(res.total)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [provider, scene, q, free])

  function setFilter(key: string, value: string) {
    const next = new URLSearchParams(params)
    if (value) next.set(key, value)
    else next.delete(key)
    setParams(next)
  }

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    setFilter('q', searchInput.trim())
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <header className="mb-8 pb-6 border-b border-ink">
        <h1 className="text-3xl font-semibold">{'\u6a21\u578b\u5e7f\u573a'}</h1>
        <p className="mt-2 text-sm text-ash leading-relaxed max-w-3xl">
          {'\u540c\u6b65\u81ea '}
          <a href="https://agicto.com/model" target="_blank" rel="noopener noreferrer" className="underline">AGICTO</a>
          {'\uff0c\u6c47\u805a 300+ \u4e3b\u6d41 AI \u5927\u6a21\u578b\u4ef7\u683c\u4e0e\u5b8c\u6574\u6587\u6863\u3002'}
        </p>
        {meta && (
          <p className="mt-2 text-xs font-mono text-silver">
            {'\u5171 '}{meta.total}{'\u4e2a\u6a21\u578b \u00b7 \u5df2\u62c9\u53d6\u6587\u6863 '}{meta.with_docs}
          </p>
        )}
      </header>

      <form onSubmit={handleSearch} className="flex gap-2 mb-6">
        <input
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          placeholder={'\u641c\u7d22\u6a21\u578b\u540d\u3001\u5382\u5546...'}
          className="flex-1 border border-ink px-3 py-2 text-sm bg-paper"
        />
        <button type="submit" className="line-border px-4 py-2 text-sm hover:bg-mist">{'\u641c\u7d22'}</button>
      </form>

      <div className="flex flex-wrap gap-2 mb-4">
        <button type="button" onClick={() => setFilter('free', '')} className={`px-3 py-1.5 text-xs border border-ink ${!free ? 'bg-ink text-paper' : 'hover:bg-mist'}`}>{'\u5168\u90e8'}</button>
        <button type="button" onClick={() => setFilter('free', '1')} className={`px-3 py-1.5 text-xs border border-ink ${free === '1' ? 'bg-ink text-paper' : 'hover:bg-mist'}`}>{'\u514d\u8d39'}</button>
        <button type="button" onClick={() => setFilter('free', '0')} className={`px-3 py-1.5 text-xs border border-ink ${free === '0' ? 'bg-ink text-paper' : 'hover:bg-mist'}`}>{'\u6536\u8d39'}</button>
      </div>

      {meta && (
        <div className="mb-6">
          <p className="text-[10px] font-mono text-silver mb-2 uppercase">{'\u4f7f\u7528\u573a\u666f'}</p>
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={() => setFilter('scene', '')} className={`px-3 py-1 text-xs border ${!scene ? 'border-ink bg-mist' : 'border-smoke hover:border-ink'}`}>{'\u5168\u90e8'}</button>
            {meta.scenes.slice(0, 10).map(([name, count]) => (
              <button key={name} type="button" onClick={() => setFilter('scene', name)} className={`px-3 py-1 text-xs border ${scene === name ? 'border-ink bg-mist' : 'border-smoke hover:border-ink'}`}>
                {name} ({count})
              </button>
            ))}
          </div>
        </div>
      )}

      {meta && (
        <div className="mb-8">
          <p className="text-[10px] font-mono text-silver mb-2 uppercase">{'\u63d0\u4f9b\u516c\u53f8'}</p>
          <div className="flex flex-wrap gap-2 max-h-28 overflow-y-auto">
            <button type="button" onClick={() => setFilter('provider', '')} className={`px-3 py-1 text-xs border ${!provider ? 'border-ink bg-mist' : 'border-smoke hover:border-ink'}`}>{'\u5168\u90e8'}</button>
            {meta.providers.slice(0, 24).map(([name, count]) => (
              <button key={name} type="button" onClick={() => setFilter('provider', name)} className={`px-3 py-1 text-xs border ${provider === name ? 'border-ink bg-mist' : 'border-smoke hover:border-ink'}`}>
                {name} ({count})
              </button>
            ))}
          </div>
        </div>
      )}

      {loading ? (
        <p className="text-sm text-silver font-mono">{'\u52a0\u8f7d\u4e2d...'}</p>
      ) : items.length ? (
        <>
          <p className="text-xs font-mono text-silver mb-4">{'\u663e\u793a '}{items.length}{' / '}{total}</p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {items.map((m) => (
              <Link
                key={m.slug}
                to={`/models/${m.slug}`}
                onMouseEnter={() => m.has_doc && api.prefetchModelMarketDoc(m.slug)}
                className="block border border-smoke hover:border-ink p-4 bg-paper hover:bg-mist transition-colors"
              >
                <div className="flex items-start justify-between gap-2">
                  <h2 className="text-base font-semibold leading-snug">{m.name}</h2>
                  {m.is_free && <span className="text-[10px] font-mono border border-green-700 text-green-800 px-1 shrink-0">{'\u514d\u8d39'}</span>}
                </div>
                <p className="text-[10px] font-mono text-silver mt-2">{m.provider || m.company_name} {'\u00b7 '}{m.scene}</p>
                {m.context_len > 0 && <p className="text-[10px] font-mono text-silver mt-1">{'\u4e0a\u4e0b\u6587 '}{(m.context_len / 1000).toFixed(0)}K</p>}
                <p className="mt-3 text-xs font-mono text-ash">
                  {'\u00a5'}{m.input_price ?? '-'}{' / M in \u00b7 \u00a5'}{m.output_price ?? '-'}{' / M out'}
                </p>
                {m.has_doc && <p className="text-[10px] text-green-800 mt-2">{'\u2713 \u5b8c\u6574\u6587\u6863'}</p>}
              </Link>
            ))}
          </div>
        </>
      ) : (
        <EmptyState title={'\u6682\u65e0\u6a21\u578b'} description={'\u8bf7\u5728\u7ba1\u7406\u540e\u53f0\u70b9\u51fb\u540c\u6b65\u6a21\u578b\u5e7f\u573a'} />
      )}
    </div>
  )
}
