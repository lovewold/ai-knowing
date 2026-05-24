import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../api/client'
import type { KnowledgeEntry } from '../../types'

export default function AdminKnowledgePage() {
  const [items, setItems] = useState<KnowledgeEntry[]>([])
  const [msg, setMsg] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [q, setQ] = useState('')
  const [kind, setKind] = useState('')
  const [searchInput, setSearchInput] = useState('')

  function reload() {
    api.getKnowledgeAdminList({ q: q || undefined, kind: kind || undefined })
      .then(setItems)
      .catch(() => setMsg('\u52a0\u8f7d\u5931\u8d25'))
  }

  useEffect(() => { reload() }, [q, kind])

  async function syncTools() {
    try {
      const r = await fetch('/api/knowledge/sync/agent-tools', { method: 'POST' })
      const d = await r.json()
      setMsg(`\u540c\u6b65 ${d.synced} \u6761 Skill`)
      reload()
    } catch {
      setMsg('\u540c\u6b65\u5931\u8d25')
    }
  }

  async function seed() {
    try {
      const r = await fetch('/api/knowledge/seed', { method: 'POST' })
      const d = await r.json()
      setMsg(`\u65b0\u589e\u79cd\u5b50 ${d.created} \u6761`)
      reload()
    } catch {
      setMsg('\u79cd\u5b50\u5931\u8d25')
    }
  }

  async function generateAll(force = false) {
    setBusy(true)
    setMsg(force ? 'AI \u6279\u91cf\u91cd\u751f\u6210\u4e2d...' : 'AI \u6279\u91cf\u751f\u6210\u6587\u6863\u4e2d...')
    try {
      const d = await api.generateKnowledgeDocs(50, force)
      setMsg(`AI \u6587\u6863: \u6210\u529f ${d.updated} / \u5904\u7406 ${d.processed}`)
      reload()
    } catch {
      setMsg('AI \u751f\u6210\u5931\u8d25')
    } finally {
      setBusy(false)
    }
  }

  async function removeItem(id: number, name: string) {
    if (!window.confirm(`\u786e\u8ba4\u5220\u9664\u300c${name}\u300d\uff1f\uff08\u9ed8\u8ba4\u9690\u85cf\uff0c\u4e0d\u7269\u7406\u5220\u9664\uff09`)) return
    try {
      await api.deleteKnowledge(id, false)
      setMsg(`\u5df2\u5220\u9664: ${name}`)
      reload()
    } catch {
      setMsg('\u5220\u9664\u5931\u8d25')
    }
  }

  const pending = items.filter((it) => it.enabled !== false && (!it.content_md || it.content_md.length < 80)).length

  return (
    <div className="p-8 max-w-5xl">
      <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-semibold mb-2">{'\u77e5\u8bc6\u5e93\u7ba1\u7406'}</h1>
          <p className="text-sm text-ash">
            {'\u589e\u5220\u6539\u67e5\u5168\u90e8\u652f\u6301\u3002\u5171 '}{items.length}{'\u6761\uff0c\u5f85\u751f\u6210\u6587\u6863 '}{pending}{'\u6761\u3002'}
          </p>
        </div>
        <Link to="/admin/knowledge/new/edit" className="line-border px-4 py-2 text-sm bg-ink text-paper hover:opacity-90 shrink-0">
          {'+ \u65b0\u589e\u6761\u76ee'}
        </Link>
      </div>

      <form
        onSubmit={(e) => { e.preventDefault(); setQ(searchInput.trim()) }}
        className="flex flex-wrap gap-2 mb-4"
      >
        <input
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          placeholder={'\u641c\u7d22\u540d\u79f0\u3001slug\u3001\u6807\u7b7e...'}
          className="flex-1 min-w-[200px] border border-smoke px-3 py-2 text-sm bg-paper"
        />
        <select value={kind} onChange={(e) => setKind(e.target.value)} className="border border-smoke px-3 py-2 text-sm bg-paper">
          <option value="">{'\u5168\u90e8\u7c7b\u578b'}</option>
          <option value="product">product</option>
          <option value="model">model</option>
          <option value="skill">skill</option>
        </select>
        <button type="submit" className="line-border px-4 py-2 text-sm hover:bg-mist">{'\u641c\u7d22'}</button>
      </form>

      <div className="flex flex-wrap gap-3 mb-6">
        <button type="button" disabled={busy} onClick={seed} className="line-border px-4 py-2 text-sm hover:bg-mist disabled:opacity-50">{'\u8fd0\u884c\u79cd\u5b50'}</button>
        <button type="button" disabled={busy} onClick={syncTools} className="line-border px-4 py-2 text-sm hover:bg-mist disabled:opacity-50">{'\u540c\u6b65 Agent \u5de5\u5177'}</button>
        <button type="button" disabled={busy} onClick={() => generateAll(false)} className="line-border px-4 py-2 text-sm hover:bg-mist disabled:opacity-50">{'AI \u6279\u91cf\u751f\u6210\u6587\u6863'}</button>
        <button type="button" disabled={busy} onClick={() => generateAll(true)} className="line-border px-4 py-2 text-sm hover:bg-mist disabled:opacity-50">{'AI \u5168\u91cf\u91cd\u751f\u6210'}</button>
      </div>

      {msg && <p className="text-xs font-mono mb-4">{msg}</p>}

      <div className="border border-ink overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-smoke bg-mist/40 text-left text-xs font-mono text-silver">
              <th className="p-3">{'\u540d\u79f0'}</th>
              <th className="p-3">{'\u7c7b\u578b'}</th>
              <th className="p-3">slug</th>
              <th className="p-3">{'\u72b6\u6001'}</th>
              <th className="p-3 text-right">{'\u64cd\u4f5c'}</th>
            </tr>
          </thead>
          <tbody>
            {items.map((it) => (
              <tr key={it.id} className="border-b border-smoke hover:bg-mist/30">
                <td className="p-3 font-medium max-w-[200px] truncate">{it.name}</td>
                <td className="p-3 font-mono text-xs text-silver">{it.kind}</td>
                <td className="p-3 font-mono text-xs text-ash max-w-[140px] truncate">{it.slug}</td>
                <td className="p-3 text-xs font-mono">
                  {it.enabled === false ? (
                    <span className="text-amber-800">{'\u5df2\u9690\u85cf'}</span>
                  ) : !it.content_md || it.content_md.length < 80 ? (
                    <span className="text-amber-800">{'\u7f3a\u6587\u6863'}</span>
                  ) : it.source_type === 'ai' ? (
                    <span className="text-green-800">AI</span>
                  ) : (
                    <span className="text-ash">{'\u5df2\u53d1\u5e03'}</span>
                  )}
                </td>
                <td className="p-3">
                  <div className="flex justify-end gap-3 text-xs">
                    <Link to={`/knowledge/${it.id}`} className="underline">{'\u67e5\u770b'}</Link>
                    <Link to={`/admin/knowledge/${it.id}/edit`} className="underline">{'\u7f16\u8f91'}</Link>
                    <button type="button" onClick={() => removeItem(it.id, it.name)} className="underline text-amber-900 hover:text-ink">
                      {'\u5220\u9664'}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {!items.length && <p className="p-6 text-sm text-silver text-center">{'\u6682\u65e0\u6761\u76ee'}</p>}
      </div>
    </div>
  )
}
