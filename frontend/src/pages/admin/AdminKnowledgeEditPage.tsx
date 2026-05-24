import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../../api/client'
import type { KnowledgeEntryWrite } from '../../types'
import KnowledgeDocEditor from '../../components/KnowledgeDocEditor'

const EMPTY: KnowledgeEntryWrite = {
  slug: '',
  kind: 'product',
  name: '',
  summary: '',
  content_md: '',
  external_url: '',
  tags: '',
  enabled: true,
}

function suggestSlug(name: string): string {
  const base = name
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9\s_-]/g, '')
    .replace(/[\s_]+/g, '-')
    .replace(/^-+|-+$/g, '')
  return base.slice(0, 120)
}

export default function AdminKnowledgeEditPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const isNew = id === 'new'
  const entryId = isNew ? null : Number(id)
  const [form, setForm] = useState<KnowledgeEntryWrite>(EMPTY)
  const [loading, setLoading] = useState(!isNew)
  const [saving, setSaving] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)
  const [slugTouched, setSlugTouched] = useState(false)

  useEffect(() => {
    if (isNew || !entryId) return
    api.getKnowledgeAdmin(entryId)
      .then((e) => {
        setForm({
          slug: e.slug,
          kind: (e.kind as KnowledgeEntryWrite['kind']) || 'product',
          name: e.name,
          summary: e.summary || '',
          content_md: e.content_md || '',
          external_url: e.external_url || '',
          tags: e.tags || '',
          enabled: e.enabled !== false,
        })
        setSlugTouched(true)
      })
      .catch(() => setMsg('\u52a0\u8f7d\u5931\u8d25'))
      .finally(() => setLoading(false))
  }, [entryId, isNew])

  function patch<K extends keyof KnowledgeEntryWrite>(key: K, value: KnowledgeEntryWrite[K]) {
    setForm((prev) => {
      const next = { ...prev, [key]: value }
      if (key === 'name' && !slugTouched && typeof value === 'string') {
        const slug = suggestSlug(value)
        if (slug) next.slug = slug
      }
      return next
    })
  }

  async function save() {
    if (!form.name.trim() || !form.slug.trim()) {
      setMsg('\u8bf7\u586b\u5199\u540d\u79f0\u4e0e slug')
      return
    }
    setSaving(true)
    setMsg(null)
    try {
      if (isNew) {
        const created = await api.createKnowledge(form)
        setMsg('\u5df2\u521b\u5efa')
        navigate(`/admin/knowledge/${created.id}/edit`, { replace: true })
      } else if (entryId) {
        await api.updateKnowledge(entryId, form)
        setMsg('\u5df2\u4fdd\u5b58\u5e76\u91cd\u65b0\u7d22\u5f15')
      }
    } catch {
      setMsg('\u4fdd\u5b58\u5931\u8d25\uff08\u68c0\u67e5 slug \u662f\u5426\u91cd\u590d\u6216\u683c\u5f0f\u4e0d\u6b63\u786e\uff09')
    } finally {
      setSaving(false)
    }
  }

  async function generate(force = false) {
    if (!entryId) {
      setMsg('\u8bf7\u5148\u4fdd\u5b58\u6761\u76ee\u518d\u751f\u6210 AI \u6587\u6863')
      return
    }
    setGenerating(true)
    setMsg(null)
    try {
      const res = await api.generateKnowledgeDoc(entryId, force)
      setForm((prev) => ({ ...prev, content_md: res.entry.content_md || '' }))
      setMsg(res.updated ? 'AI \u6587\u6863\u5df2\u751f\u6210' : '\u672a\u66f4\u65b0')
    } catch {
      setMsg('AI \u751f\u6210\u5931\u8d25\uff0c\u8bf7\u68c0\u67e5 LLM \u914d\u7f6e')
    } finally {
      setGenerating(false)
    }
  }

  if (loading) return <p className="p-8 text-sm text-silver font-mono">{'\u52a0\u8f7d\u4e2d...'}</p>

  return (
    <div className="p-6 max-w-5xl">
      <Link to="/admin/knowledge" className="text-xs font-mono text-ash hover:text-ink underline">{'\u2190 \u77e5\u8bc6\u5e93\u7ba1\u7406'}</Link>
      <header className="mt-4 mb-6 pb-4 border-b border-ink flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-[10px] font-mono text-silver uppercase">{isNew ? 'NEW' : `ID ${entryId}`}</p>
          <h1 className="text-2xl font-semibold mt-1">{isNew ? '\u65b0\u589e\u6761\u76ee' : form.name || '\u7f16\u8f91\u6761\u76ee'}</h1>
        </div>
        <div className="flex flex-wrap gap-2">
          {!isNew && (
            <>
              <button type="button" disabled={generating || saving} onClick={() => generate(false)} className="line-border px-3 py-2 text-sm hover:bg-mist disabled:opacity-50">
                {generating ? 'AI \u751f\u6210\u4e2d\u2026' : 'AI \u751f\u6210\u6587\u6863'}
              </button>
              <button type="button" disabled={generating || saving} onClick={() => generate(true)} className="line-border px-3 py-2 text-sm hover:bg-mist disabled:opacity-50">
                {'\u91cd\u65b0\u751f\u6210'}
              </button>
              {entryId && (
                <Link to={`/knowledge/${entryId}`} className="line-border px-3 py-2 text-sm hover:bg-mist inline-flex items-center">{'\u9884\u89c8'}</Link>
              )}
            </>
          )}
          <button type="button" disabled={saving || generating} onClick={save} className="line-border px-3 py-2 text-sm bg-ink text-paper hover:opacity-90 disabled:opacity-50">
            {saving ? '\u4fdd\u5b58\u4e2d\u2026' : isNew ? '\u521b\u5efa' : '\u4fdd\u5b58'}
          </button>
        </div>
      </header>

      {msg && <p className="text-xs font-mono mb-4 text-ash">{msg}</p>}

      <div className="grid md:grid-cols-2 gap-4 mb-6">
        <label className="block text-sm">
          <span className="text-xs font-mono text-silver">{'\u540d\u79f0 *'}</span>
          <input value={form.name} onChange={(e) => patch('name', e.target.value)} className="mt-1 w-full border border-smoke px-3 py-2 bg-paper" />
        </label>
        <label className="block text-sm">
          <span className="text-xs font-mono text-silver">{'slug *'}</span>
          <input
            value={form.slug}
            onChange={(e) => { setSlugTouched(true); patch('slug', e.target.value) }}
            placeholder="my-tool-name"
            className="mt-1 w-full border border-smoke px-3 py-2 bg-paper font-mono text-sm"
          />
        </label>
        <label className="block text-sm">
          <span className="text-xs font-mono text-silver">{'\u7c7b\u578b'}</span>
          <select value={form.kind} onChange={(e) => patch('kind', e.target.value as KnowledgeEntryWrite['kind'])} className="mt-1 w-full border border-smoke px-3 py-2 bg-paper">
            <option value="product">product</option>
            <option value="model">model</option>
            <option value="skill">skill</option>
          </select>
        </label>
        <label className="block text-sm">
          <span className="text-xs font-mono text-silver">{'\u6807\u7b7e\uff08\u9017\u53f7\u5206\u9694\uff09'}</span>
          <input value={form.tags || ''} onChange={(e) => patch('tags', e.target.value)} className="mt-1 w-full border border-smoke px-3 py-2 bg-paper" />
        </label>
        <label className="block text-sm md:col-span-2">
          <span className="text-xs font-mono text-silver">{'\u5b98\u65b9\u94fe\u63a5'}</span>
          <input value={form.external_url || ''} onChange={(e) => patch('external_url', e.target.value)} className="mt-1 w-full border border-smoke px-3 py-2 bg-paper" />
        </label>
        <label className="block text-sm md:col-span-2">
          <span className="text-xs font-mono text-silver">{'\u6458\u8981'}</span>
          <textarea value={form.summary || ''} onChange={(e) => patch('summary', e.target.value)} rows={2} className="mt-1 w-full border border-smoke px-3 py-2 bg-paper leading-relaxed" />
        </label>
        <label className="flex items-center gap-2 text-sm md:col-span-2">
          <input type="checkbox" checked={form.enabled !== false} onChange={(e) => patch('enabled', e.target.checked)} />
          <span>{'\u5728\u524d\u53f0\u663e\u793a\uff08\u542f\u7528\uff09'}</span>
        </label>
      </div>

      <p className="text-xs font-mono text-silver mb-2 uppercase">{'\u6559\u7a0b\u6587\u6863\uff08Markdown \u5bcc\u6587\u672c\uff09'}</p>
      <KnowledgeDocEditor value={form.content_md || ''} onChange={(v) => patch('content_md', v)} height={480} />

      <div className="mt-4 flex flex-wrap gap-2">
        <button type="button" disabled={saving} onClick={save} className="line-border px-4 py-2 text-sm bg-ink text-paper disabled:opacity-50">
          {isNew ? '\u521b\u5efa\u6761\u76ee' : '\u4fdd\u5b58\u5e76\u7d22\u5f15'}
        </button>
        <button type="button" onClick={() => navigate('/admin/knowledge')} className="line-border px-4 py-2 text-sm hover:bg-mist">
          {'\u8fd4\u56de\u5217\u8868'}
        </button>
      </div>
    </div>
  )
}
