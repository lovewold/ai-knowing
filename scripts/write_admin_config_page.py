# -*- coding: utf-8 -*-
from pathlib import Path

CONTENT = r'''import { useEffect, useState, type FormEvent } from 'react'
import {
  adminApi,
  type BriefingConfig,
  type DouyinCreator,
  type SourceConfig,
} from '../../api/admin'

const SOURCE_TYPES = ['rss', 'arxiv', 'hackernews', 'github_trending', 'github_search'] as const

const emptySource = (): SourceConfig => ({
  id: '',
  name: '',
  type: 'rss',
  weight: 50,
  language: 'zh',
  enabled: true,
  url: '',
})

const emptyCreator = (): DouyinCreator => ({
  name: '',
  profile_url: '',
  focus: '',
  reason: '',
})

const defaultBriefing: BriefingConfig = {
  window_hours: 24,
  max_articles: 12,
  min_score: 0.68,
  include_high_signal: true,
  include_medium_zh: true,
  medium_zh_min_score: 0.52,
  prefer_localized: true,
  overview_max_tokens: 280,
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block text-xs text-ash">
      {label}
      <motion.div className="mt-1">{children}</div>
    </label>
  )
}

function BriefingTab({ msg, setMsg }: { msg: string | null; setMsg: (v: string | null) => void }) {
  const [form, setForm] = useState<BriefingConfig>(defaultBriefing)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    adminApi.getBriefingConfig()
      .then((c) => setForm({ ...defaultBriefing, ...c }))
      .catch(() => setMsg('\u52a0\u8f7d\u5931\u8d25\uff0c\u8bf7\u68c0\u67e5 Token'))
      .finally(() => setLoading(false))
  }, [setMsg])

  async function save(e: FormEvent) {
    e.preventDefault()
    try {
      await adminApi.saveBriefingConfig(form)
      setMsg('\u6668\u62a5\u914d\u7f6e\u5df2\u4fdd\u5b58')
    } catch {
      setMsg('\u4fdd\u5b58\u5931\u8d25')
    }
  }

  if (loading) return <p className="text-sm text-silver font-mono">\u52a0\u8f7d\u4e2d...</p>

  return (
    <form onSubmit={save} className="space-y-6 max-w-xl">
      <p className="text-sm text-ash">\u8bbe\u7f6e\u6bcf\u65e5\u6668\u62a5\u7684\u7b5b\u9009\u6761\u4ef6\u4e0e AI \u5bfc\u8bed\u957f\u5ea6\u3002</p>
      <div className="grid grid-cols-2 gap-4">
        <Field label="\u7edf\u8ba1\u65f6\u95f4\u7a97\uff08\u5c0f\u65f6\uff09">
          <input type="number" min={1} max={168} className="w-full border border-smoke px-2 py-1.5 text-sm"
            value={form.window_hours} onChange={(e) => setForm({ ...form, window_hours: Number(e.target.value) })} />
        </Field>
        <Field label="\u6700\u591a\u7eb3\u5165\u6761\u6570">
          <input type="number" min={1} max={50} className="w-full border border-smoke px-2 py-1.5 text-sm"
            value={form.max_articles} onChange={(e) => setForm({ ...form, max_articles: Number(e.target.value) })} />
        </Field>
        <Field label="\u6700\u4f4e\u4fe1\u566a\u5206">
          <input type="number" min={0} max={1} step={0.01} className="w-full border border-smoke px-2 py-1.5 text-sm"
            value={form.min_score} onChange={(e) => setForm({ ...form, min_score: Number(e.target.value) })} />
        </Field>
        <Field label="\u4e2d\u6587\u6e90\u4e2d\u4fe1\u53f7\u6700\u4f4e\u5206">
          <input type="number" min={0} max={1} step={0.01} className="w-full border border-smoke px-2 py-1.5 text-sm"
            value={form.medium_zh_min_score} onChange={(e) => setForm({ ...form, medium_zh_min_score: Number(e.target.value) })} />
        </Field>
        <Field label="AI \u5bfc\u8bed\u5b57\u6570\u4e0a\u9650">
          <input type="number" min={50} max={2000} className="w-full border border-smoke px-2 py-1.5 text-sm"
            value={form.overview_max_tokens} onChange={(e) => setForm({ ...form, overview_max_tokens: Number(e.target.value) })} />
        </Field>
      </div>
      <div className="flex flex-col gap-2 text-sm">
        <label className="flex items-center gap-2">
          <input type="checkbox" checked={form.include_high_signal}
            onChange={(e) => setForm({ ...form, include_high_signal: e.target.checked })} />
          \u7eb3\u5165\u9ad8\u4fe1\u53f7\u8d44\u8baf
        </label>
        <label className="flex items-center gap-2">
          <input type="checkbox" checked={form.include_medium_zh}
            onChange={(e) => setForm({ ...form, include_medium_zh: e.target.checked })} />
          \u7eb3\u5165\u4e2d\u6587\u6e90\u4e2d\u4fe1\u53f7\u8d44\u8baf
        </label>
        <label className="flex items-center gap-2">
          <input type="checkbox" checked={form.prefer_localized}
            onChange={(e) => setForm({ ...form, prefer_localized: e.target.checked })} />
          \u4f18\u5148\u5df2\u6709\u4e2d\u6587\u6458\u8981\u7684\u6761\u76ee
        </label>
      </div>
      <button type="submit" className="px-6 py-2 border border-ink text-sm hover:bg-ink hover:text-paper">\u4fdd\u5b58\u6668\u62a5\u914d\u7f6e</button>
    </form>
  )
}

function CreatorsTab({ msg, setMsg }: { msg: string | null; setMsg: (v: string | null) => void }) {
  const [creators, setCreators] = useState<DouyinCreator[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    adminApi.getCreators()
      .then(setCreators)
      .catch(() => setMsg('\u52a0\u8f7d\u5931\u8d25\uff0c\u8bf7\u68c0\u67e5 Token'))
      .finally(() => setLoading(false))
  }, [setMsg])

  function update(i: number, patch: Partial<DouyinCreator>) {
    setCreators(creators.map((c, idx) => (idx === i ? { ...c, ...patch } : c)))
  }

  async function save() {
    const valid = creators.filter((c) => c.name.trim() && c.profile_url.trim())
    try {
      await adminApi.saveCreators(valid)
      setCreators(valid)
      setMsg('\u535a\u4e3b\u5217\u8868\u5df2\u4fdd\u5b58')
    } catch {
      setMsg('\u4fdd\u5b58\u5931\u8d25')
    }
  }

  if (loading) return <p className="text-sm text-silver font-mono">\u52a0\u8f7d\u4e2d...</p>

  return (
    <div className="space-y-4 max-w-2xl">
      <p className="text-sm text-ash">\u7ba1\u7406\u6668\u62a5\u300c\u6296\u97f3\u535a\u4e3b\u63a8\u8350\u300d\u677f\u5757\uff0c\u586b\u5199\u540d\u79f0\u3001\u4e3b\u9875\u94fe\u63a5\u4e0e\u63a8\u8350\u7406\u7531\u5373\u53ef\u3002</p>
      {creators.map((c, i) => (
        <div key={i} className="border border-ink p-4 space-y-3">
          <motion.div className="flex justify-between items-center">
            <span className="text-xs font-mono text-silver">\u535a\u4e3b {i + 1}</span>
            <button type="button" onClick={() => setCreators(creators.filter((_, idx) => idx !== i))}
              className="text-xs text-red-700 underline">\u5220\u9664</button>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Field label="\u540d\u79f0">
              <input className="w-full border border-smoke px-2 py-1.5 text-sm" value={c.name}
                onChange={(e) => update(i, { name: e.target.value })} />
            </Field>
            <Field label="\u4e3b\u9875\u94fe\u63a5">
              <input className="w-full border border-smoke px-2 py-1.5 text-sm" value={c.profile_url}
                onChange={(e) => update(i, { profile_url: e.target.value })} />
            </Field>
          </div>
          <Field label="\u5185\u5bb9\u65b9\u5411">
            <input className="w-full border border-smoke px-2 py-1.5 text-sm" value={c.focus}
              onChange={(e) => update(i, { focus: e.target.value })} />
          </Field>
          <Field label="\u63a8\u8350\u7406\u7531">
            <input className="w-full border border-smoke px-2 py-1.5 text-sm" value={c.reason}
              onChange={(e) => update(i, { reason: e.target.value })} />
          </Field>
        </div>
      ))}
      <div className="flex gap-3">
        <button type="button" onClick={() => setCreators([...creators, emptyCreator()])}
          className="px-4 py-2 border border-ink text-sm hover:bg-mist">+ \u6dfb\u52a0\u535a\u4e3b</button>
        <button type="button" onClick={save}
          className="px-6 py-2 border border-ink text-sm hover:bg-ink hover:text-paper">\u4fdd\u5b58\u535a\u4e3b\u5217\u8868</button>
      </div>
    </div>
  )
}

function SourcesTab({ msg, setMsg }: { msg: string | null; setMsg: (v: string | null) => void }) {
  const [sources, setSources] = useState<SourceConfig[]>([])
  const [editId, setEditId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    adminApi.getSources()
      .then(setSources)
      .catch(() => setMsg('\u52a0\u8f7d\u5931\u8d25\uff0c\u8bf7\u68c0\u67e5 Token'))
      .finally(() => setLoading(false))
  }, [setMsg])

  const editing = sources.find((s) => s.id === editId)

  function updateEditing(patch: Partial<SourceConfig>) {
    if (!editId) return
    setSources(sources.map((s) => (s.id === editId ? { ...s, ...patch } : s)))
  }

  async function saveAll() {
    try {
      await adminApi.saveSources(sources)
      setMsg('\u6570\u636e\u6e90\u5df2\u4fdd\u5b58\uff0c\u4e0b\u6b21\u6293\u53d6\u751f\u6548')
    } catch {
      setMsg('\u4fdd\u5b58\u5931\u8d25\uff0c\u8bf7\u68c0\u67e5 ID \u662f\u5426\u91cd\u590d')
    }
  }

  function addSource() {
    const s = emptySource()
    s.id = `source-${Date.now()}`
    s.name = '\u65b0\u6570\u636e\u6e90'
    setSources([...sources, s])
    setEditId(s.id)
  }

  function removeSource(id: string) {
    if (!confirm('\u786e\u5b9a\u5220\u9664\u6b64\u6570\u636e\u6e90\uff1f')) return
    setSources(sources.filter((s) => s.id !== id))
    if (editId === id) setEditId(null)
  }

  if (loading) return <p className="text-sm text-silver font-mono">\u52a0\u8f7d\u4e2d...</p>

  return (
    <div className="space-y-4">
      <p className="text-sm text-ash">\u70b9\u51fb\u6570\u636e\u6e90\u540d\u79f0\u7f16\u8f91\u8be6\u60c5\uff0c\u53ef\u5f00\u5173\u542f\u7528\u6216\u8c03\u6574\u6743\u91cd\u3002</p>
      <div className="border border-ink divide-y divide-smoke">
        {sources.map((s) => (
          <div key={s.id} className="p-3 flex items-center gap-4 hover:bg-mist">
            <input type="checkbox" checked={s.enabled}
              onChange={(e) => setSources(sources.map((x) => x.id === s.id ? { ...x, enabled: e.target.checked } : x))} />
            <button type="button" onClick={() => setEditId(editId === s.id ? null : s.id)}
              className="flex-1 text-left text-sm font-medium">{s.name}</button>
            <span className="text-xs font-mono text-silver">{s.type}</span>
            <span className="text-xs font-mono w-8 text-right">{s.weight}</span>
            <button type="button" onClick={() => removeSource(s.id)} className="text-xs text-red-700 underline">\u5220\u9664</button>
          </div>
        ))}
      </motion.div>

      {editing && (
        <div className="border border-ink p-4 space-y-3 max-w-xl bg-mist/30">
          <p className="text-sm font-medium">\u7f16\u8f91\uff1a{editing.name}</p>
          <motion.div className="grid grid-cols-2 gap-3">
            <Field label="ID\uff08\u82f1\u6587\u552f\u4e00\u6807\u8bc6\uff09">
              <input className="w-full border border-smoke px-2 py-1.5 text-sm font-mono" value={editing.id}
                onChange={(e) => {
                  const newId = e.target.value
                  setSources(sources.map((s) => s.id === editId ? { ...s, id: newId } : s))
                  setEditId(newId)
                }} />
            </Field>
            <Field label="\u663e\u793a\u540d\u79f0">
              <input className="w-full border border-smoke px-2 py-1.5 text-sm" value={editing.name}
                onChange={(e) => updateEditing({ name: e.target.value })} />
            </Field>
            <Field label="\u7c7b\u578b">
              <select className="w-full border border-smoke px-2 py-1.5 text-sm" value={editing.type}
                onChange={(e) => updateEditing({ type: e.target.value })}>
                {SOURCE_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </Field>
            <Field label="\u6743\u91cd (0-100)">
              <input type="number" min={0} max={100} className="w-full border border-smoke px-2 py-1.5 text-sm"
                value={editing.weight} onChange={(e) => updateEditing({ weight: Number(e.target.value) })} />
            </Field>
            <Field label="\u8bed\u8a00">
              <select className="w-full border border-smoke px-2 py-1.5 text-sm" value={editing.language}
                onChange={(e) => updateEditing({ language: e.target.value })}>
                <option value="zh">zh</option>
                <option value="en">en</option>
              </select>
            </Field>
          </div>
          {editing.type === 'rss' && (
            <Field label="RSS URL">
              <input className="w-full border border-smoke px-2 py-1.5 text-sm font-mono" value={editing.url || ''}
                onChange={(e) => updateEditing({ url: e.target.value })} />
            </Field>
          )}
          {editing.type === 'arxiv' && (
            <Field label="ArXiv \u5206\u7c7b">
              <input className="w-full border border-smoke px-2 py-1.5 text-sm font-mono" value={editing.category || ''}
                onChange={(e) => updateEditing({ category: e.target.value })} placeholder="cs.AI" />
            </Field>
          )}
          {editing.type === 'github_search' && (
            <Field label="GitHub \u641c\u7d22\u8bed\u53e5">
              <input className="w-full border border-smoke px-2 py-1.5 text-sm font-mono" value={editing.query || ''}
                onChange={(e) => updateEditing({ query: e.target.value })} />
            </Field>
          )}
          {editing.type === 'hackernews' && (
            <Field label="\u8fc7\u6ee4\u6761\u4ef6\uff08\u53ef\u9009\uff0c\u5982 show\uff09">
              <input className="w-full border border-smoke px-2 py-1.5 text-sm font-mono" value={editing.filter || ''}
                onChange={(e) => updateEditing({ filter: e.target.value || undefined })} />
            </Field>
          )}
        </div>
      )}

      <div className="flex gap-3">
        <button type="button" onClick={addSource} className="px-4 py-2 border border-ink text-sm hover:bg-mist">+ \u6dfb\u52a0\u6570\u636e\u6e90</button>
        <button type="button" onClick={saveAll} className="px-6 py-2 border border-ink text-sm hover:bg-ink hover:text-paper">\u4fdd\u5b58\u6240\u6709\u6570\u636e\u6e90</button>
      </div>
    </div>
  )
}

export default function AdminConfigPage() {
  const [tab, setTab] = useState<'briefing' | 'creators' | 'sources'>('briefing')
  const [msg, setMsg] = useState<string | null>(null)

  const tabs = [
    { key: 'briefing' as const, label: '\u6668\u62a5\u8bbe\u7f6e' },
    { key: 'creators' as const, label: '\u6296\u97f3\u535a\u4e3b' },
    { key: 'sources' as const, label: '\u6570\u636e\u6e90' },
  ]

  return (
    <div className="p-8 max-w-4xl">
      <h1 className="font-serif text-2xl font-semibold mb-2">\u914d\u7f6e\u7ba1\u7406</h1>
      <p className="text-sm text-ash mb-6">\u8868\u5355\u5316\u7f16\u8f91\uff0c\u65e0\u9700\u624b\u52a8\u6539 JSON</p>
      <div className="flex gap-2 mb-6 border-b border-ink">
        {tabs.map(({ key, label }) => (
          <button key={key} type="button" onClick={() => { setTab(key); setMsg(null) }}
            className={`px-4 py-2 text-sm border-b-2 -mb-px ${tab === key ? 'border-ink font-medium' : 'border-transparent text-ash'}`}>
            {label}
          </button>
        ))}
      </div>
      {msg && <p className="text-xs font-mono mb-4 text-ash">{msg}</p>}
      {tab === 'briefing' && <BriefingTab msg={msg} setMsg={setMsg} />}
      {tab === 'creators' && <CreatorsTab msg={msg} setMsg={setMsg} />}
      {tab === 'sources' && <SourcesTab msg={msg} setMsg={setMsg} />}
    </div>
  )
}
'''

def main():
    text = CONTENT.encode('utf-8').decode('unicode_escape')
    while '<motion.div' in text:
        text = text.replace('<motion.div', '<motion.div')
        text = text.replace('<motion.div', '<div')
    text = text.replace('</motion.div>', '</div>')
    text = text.replace('<motion.div className="mt-1">', '<div className="mt-1">')
    path = Path(__file__).resolve().parent.parent / 'frontend' / 'src' / 'pages' / 'admin' / 'AdminConfigPage.tsx'
    path.write_text(text, encoding='utf-8', newline='\n')
    print('wrote', path)


if __name__ == '__main__':
    main()
