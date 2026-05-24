import { useEffect, useState, type FormEvent, type ReactNode } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  adminApi,
  type BriefingConfig,
  type DouyinCreator,
  type SourceConfig,
} from '../../api/admin'

const SOURCE_TYPES = [
  'rss', 'arxiv', 'hackernews', 'github_trending', 'github_search',
  'firecrawl', 'twitterapi_io', 'http_json',
] as const

const emptySource = (): SourceConfig => ({
  id: '',
  name: '',
  type: 'rss',
  weight: 50,
  language: 'zh',
  enabled: true,
  url: '',
  color: '',
})

const emptyCreator = (): DouyinCreator => ({
  name: '',
  profile_url: '',
  focus: '',
  reason: '',
})

const defaultBriefing: BriefingConfig = {
  window_hours: 24,
  max_articles: 18,
  min_score: 68,
  include_high_signal: true,
  include_medium_zh: true,
  medium_zh_min_score: 52,
  prefer_localized: true,
  overview_max_tokens: 900,
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block text-xs text-ash">
      {label}
      <div className="mt-1">{children}</div>
    </label>
  )
}

function BriefingTab({ setMsg }: { setMsg: (v: string | null) => void }) {
  const [form, setForm] = useState<BriefingConfig>(defaultBriefing)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    adminApi.getBriefingConfig()
      .then((c) => setForm({ ...defaultBriefing, ...c }))
      .catch(() => setMsg('加载失败，请检查 Token'))
      .finally(() => setLoading(false))
  }, [setMsg])

  async function save(e: FormEvent) {
    e.preventDefault()
    try {
      await adminApi.saveBriefingConfig(form)
      setMsg('晨报配置已保存')
    } catch {
      setMsg('保存失败')
    }
  }

  if (loading) return <p className="text-sm text-silver font-mono">加载中...</p>

  return (
    <form onSubmit={save} className="space-y-6 max-w-xl">
      <p className="text-sm text-ash">设置每日晨报的筛选条件与 AI 导语长度。</p>
      <div className="grid grid-cols-2 gap-4">
        <Field label="统计时间窗（小时）">
          <input type="number" min={1} max={168} className="w-full border border-smoke px-2 py-1.5 text-sm"
            value={form.window_hours} onChange={(e) => setForm({ ...form, window_hours: Number(e.target.value) })} />
        </Field>
        <Field label="最多纳入条数">
          <input type="number" min={1} max={50} className="w-full border border-smoke px-2 py-1.5 text-sm"
            value={form.max_articles} onChange={(e) => setForm({ ...form, max_articles: Number(e.target.value) })} />
        </Field>
        <Field label="最低信噪分">
          <input type="number" min={0} max={1} step={0.01} className="w-full border border-smoke px-2 py-1.5 text-sm"
            value={form.min_score} onChange={(e) => setForm({ ...form, min_score: Number(e.target.value) })} />
        </Field>
        <Field label="中文源中信号最低分">
          <input type="number" min={0} max={1} step={0.01} className="w-full border border-smoke px-2 py-1.5 text-sm"
            value={form.medium_zh_min_score} onChange={(e) => setForm({ ...form, medium_zh_min_score: Number(e.target.value) })} />
        </Field>
        <Field label="AI 导语字数上限">
          <input type="number" min={50} max={2000} className="w-full border border-smoke px-2 py-1.5 text-sm"
            value={form.overview_max_tokens} onChange={(e) => setForm({ ...form, overview_max_tokens: Number(e.target.value) })} />
        </Field>
      </div>
      <div className="flex flex-col gap-2 text-sm">
        <label className="flex items-center gap-2">
          <input type="checkbox" checked={form.include_high_signal}
            onChange={(e) => setForm({ ...form, include_high_signal: e.target.checked })} />
          纳入高信号资讯
        </label>
        <label className="flex items-center gap-2">
          <input type="checkbox" checked={form.include_medium_zh}
            onChange={(e) => setForm({ ...form, include_medium_zh: e.target.checked })} />
          纳入中文源中信号资讯
        </label>
        <label className="flex items-center gap-2">
          <input type="checkbox" checked={form.prefer_localized}
            onChange={(e) => setForm({ ...form, prefer_localized: e.target.checked })} />
          优先已有中文摘要的条目
        </label>
      </div>
      <button type="submit" className="px-6 py-2 border border-ink text-sm hover:bg-ink hover:text-paper">保存晨报配置</button>
    </form>
  )
}

function CreatorsTab({ setMsg }: { setMsg: (v: string | null) => void }) {
  const [creators, setCreators] = useState<DouyinCreator[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    adminApi.getCreators()
      .then(setCreators)
      .catch(() => setMsg('加载失败，请检查 Token'))
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
      setMsg('博主列表已保存')
    } catch {
      setMsg('保存失败')
    }
  }

  if (loading) return <p className="text-sm text-silver font-mono">加载中...</p>

  return (
    <div className="space-y-4 max-w-2xl">
      <p className="text-sm text-ash">管理晨报「抖音博主推荐」板块，填写名称、主页链接与推荐理由即可。</p>
      {creators.map((c, i) => (
        <div key={i} className="border border-ink p-4 space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-xs font-mono text-silver">博主 {i + 1}</span>
            <button type="button" onClick={() => setCreators(creators.filter((_, idx) => idx !== i))}
              className="text-xs text-red-700 underline">删除</button>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Field label="名称">
              <input className="w-full border border-smoke px-2 py-1.5 text-sm" value={c.name}
                onChange={(e) => update(i, { name: e.target.value })} />
            </Field>
            <Field label="主页链接">
              <input className="w-full border border-smoke px-2 py-1.5 text-sm" value={c.profile_url}
                onChange={(e) => update(i, { profile_url: e.target.value })} />
            </Field>
          </div>
          <Field label="内容方向">
            <input className="w-full border border-smoke px-2 py-1.5 text-sm" value={c.focus}
              onChange={(e) => update(i, { focus: e.target.value })} />
          </Field>
          <Field label="推荐理由">
            <input className="w-full border border-smoke px-2 py-1.5 text-sm" value={c.reason}
              onChange={(e) => update(i, { reason: e.target.value })} />
          </Field>
        </div>
      ))}
      <div className="flex gap-3">
        <button type="button" onClick={() => setCreators([...creators, emptyCreator()])}
          className="px-4 py-2 border border-ink text-sm hover:bg-mist">+ 添加博主</button>
        <button type="button" onClick={save}
          className="px-6 py-2 border border-ink text-sm hover:bg-ink hover:text-paper">保存博主列表</button>
      </div>
    </div>
  )
}

function SourcesTab({ setMsg }: { setMsg: (v: string | null) => void }) {
  const [sources, setSources] = useState<SourceConfig[]>([])
  const [editId, setEditId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    adminApi.getSources()
      .then(setSources)
      .catch(() => setMsg('加载失败，请检查 Token'))
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
      setMsg('数据源已保存，下次抓取生效')
    } catch {
      setMsg('保存失败，请检查 ID 是否重复')
    }
  }

  function addSource() {
    const s = emptySource()
    s.id = `source-${Date.now()}`
    s.name = '新数据源'
    setSources([...sources, s])
    setEditId(s.id)
  }

  function removeSource(id: string) {
    if (!confirm('确定删除此数据源？')) return
    setSources(sources.filter((s) => s.id !== id))
    if (editId === id) setEditId(null)
  }

  if (loading) return <p className="text-sm text-silver font-mono">加载中...</p>

  return (
    <div className="space-y-4">
      <p className="text-sm text-ash">点击数据源名称编辑详情，可开关启用或调整权重。</p>
      <div className="border border-ink divide-y divide-smoke">
        {sources.map((s) => (
          <div key={s.id} className="p-3 flex items-center gap-4 hover:bg-mist">
            <input type="checkbox" checked={s.enabled}
              onChange={(e) => setSources(sources.map((x) => x.id === s.id ? { ...x, enabled: e.target.checked } : x))} />
            <button type="button" onClick={() => setEditId(editId === s.id ? null : s.id)}
              className="flex-1 text-left text-sm font-medium flex items-center gap-2">
              {s.color && /^#[0-9a-fA-F]{6}$/.test(s.color) && (
                <span className="w-2.5 h-2.5 rounded-full shrink-0 border border-black/10" style={{ backgroundColor: s.color }} />
              )}
              {s.name}
            </button>
            <span className="text-xs font-mono text-silver">{s.type}</span>
            <span className="text-xs font-mono w-8 text-right">{s.weight}</span>
            <button type="button" onClick={() => removeSource(s.id)} className="text-xs text-red-700 underline">删除</button>
          </div>
        ))}
      </div>

      {editing && (
        <div className="border border-ink p-4 space-y-3 max-w-xl bg-mist/30">
          <p className="text-sm font-medium">编辑：{editing.name}</p>
          <div className="grid grid-cols-2 gap-3">
            <Field label="ID（英文唯一标识）">
              <input className="w-full border border-smoke px-2 py-1.5 text-sm font-mono" value={editing.id}
                onChange={(e) => {
                  const newId = e.target.value
                  setSources(sources.map((s) => s.id === editId ? { ...s, id: newId } : s))
                  setEditId(newId)
                }} />
            </Field>
            <Field label="显示名称">
              <input className="w-full border border-smoke px-2 py-1.5 text-sm" value={editing.name}
                onChange={(e) => updateEditing({ name: e.target.value })} />
            </Field>
            <Field label="类型">
              <select className="w-full border border-smoke px-2 py-1.5 text-sm" value={editing.type}
                onChange={(e) => updateEditing({ type: e.target.value })}>
                {SOURCE_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </Field>
            <Field label="权重 (0-100)">
              <input type="number" min={0} max={100} className="w-full border border-smoke px-2 py-1.5 text-sm"
                value={editing.weight} onChange={(e) => updateEditing({ weight: Number(e.target.value) })} />
            </Field>
            <Field label="语言">
              <select className="w-full border border-smoke px-2 py-1.5 text-sm" value={editing.language}
                onChange={(e) => updateEditing({ language: e.target.value })}>
                <option value="zh">zh</option>
                <option value="en">en</option>
              </select>
            </Field>
            <Field label="品牌色 (#hex)">
              <input className="w-full border border-smoke px-2 py-1.5 text-sm font-mono" value={editing.color || ''}
                onChange={(e) => updateEditing({ color: e.target.value || undefined })} placeholder="#ff6498" />
            </Field>
          </div>
          {(editing.type === 'rss' || editing.type === 'firecrawl' || editing.type === 'http_json') && (
            <Field label={editing.type === 'firecrawl' ? '目标页面 URL' : editing.type === 'http_json' ? 'JSON API URL' : 'RSS URL'}>
              <input className="w-full border border-smoke px-2 py-1.5 text-sm font-mono" value={editing.url || ''}
                onChange={(e) => updateEditing({ url: e.target.value })} />
            </Field>
          )}
          {editing.type === 'http_json' && (
            <Field label="解析器 (bilibili / v2ex / reddit)">
              <input className="w-full border border-smoke px-2 py-1.5 text-sm font-mono" value={editing.parser || ''}
                onChange={(e) => updateEditing({ parser: e.target.value || undefined })} />
            </Field>
          )}
          {editing.type === 'twitterapi_io' && (
            <>
              <Field label="搜索语句 (Twitter 高级语法)">
                <input className="w-full border border-smoke px-2 py-1.5 text-sm font-mono" value={editing.query || ''}
                  onChange={(e) => updateEditing({ query: e.target.value })} />
              </Field>
              <div className="grid grid-cols-2 gap-3">
                <Field label="排序 (Top / Latest)">
                  <input className="w-full border border-smoke px-2 py-1.5 text-sm font-mono" value={editing.filter || 'Top'}
                    onChange={(e) => updateEditing({ filter: e.target.value || undefined })} />
                </Field>
                <Field label="最低互动量">
                  <input type="number" min={0} className="w-full border border-smoke px-2 py-1.5 text-sm"
                    value={editing.min_engagement ?? 100}
                    onChange={(e) => updateEditing({ min_engagement: Number(e.target.value) })} />
                </Field>
              </div>
            </>
          )}
          {editing.type === 'arxiv' && (
            <Field label="ArXiv 分类">
              <input className="w-full border border-smoke px-2 py-1.5 text-sm font-mono" value={editing.category || ''}
                onChange={(e) => updateEditing({ category: e.target.value })} placeholder="cs.AI" />
            </Field>
          )}
          {editing.type === 'github_search' && (
            <Field label="GitHub 搜索语句">
              <input className="w-full border border-smoke px-2 py-1.5 text-sm font-mono" value={editing.query || ''}
                onChange={(e) => updateEditing({ query: e.target.value })} />
            </Field>
          )}
          {editing.type === 'hackernews' && (
            <Field label="过滤条件（可选，如 show）">
              <input className="w-full border border-smoke px-2 py-1.5 text-sm font-mono" value={editing.filter || ''}
                onChange={(e) => updateEditing({ filter: e.target.value || undefined })} />
            </Field>
          )}
        </div>
      )}

      <div className="flex gap-3">
        <button type="button" onClick={addSource} className="px-4 py-2 border border-ink text-sm hover:bg-mist">+ 添加数据源</button>
        <button type="button" onClick={saveAll} className="px-6 py-2 border border-ink text-sm hover:bg-ink hover:text-paper">保存所有数据源</button>
      </div>
    </div>
  )
}

export default function AdminConfigPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const tabParam = searchParams.get('tab')
  const initialTab = tabParam === 'sources' || tabParam === 'creators' || tabParam === 'briefing'
    ? tabParam
    : 'briefing'
  const [tab, setTab] = useState<'briefing' | 'creators' | 'sources'>(initialTab)
  const [msg, setMsg] = useState<string | null>(null)

  useEffect(() => {
    if (tabParam === 'sources' || tabParam === 'creators' || tabParam === 'briefing') {
      setTab(tabParam)
    }
  }, [tabParam])

  function selectTab(key: 'briefing' | 'creators' | 'sources') {
    setTab(key)
    setMsg(null)
    setSearchParams(key === 'briefing' ? {} : { tab: key })
  }

  const tabs = [
    { key: 'briefing' as const, label: '晨报设置' },
    { key: 'creators' as const, label: '抖音博主' },
    { key: 'sources' as const, label: '数据源' },
  ]

  return (
    <div className="p-8 max-w-4xl">
      <h1 className="font-serif text-2xl font-semibold mb-2">配置管理</h1>
      <p className="text-sm text-ash mb-6">表单化编辑，无需手动改 JSON</p>
      <div className="flex gap-2 mb-6 border-b border-ink">
        {tabs.map(({ key, label }) => (
          <button key={key} type="button" onClick={() => selectTab(key)}
            className={`px-4 py-2 text-sm border-b-2 -mb-px ${tab === key ? 'border-ink font-medium' : 'border-transparent text-ash'}`}>
            {label}
          </button>
        ))}
      </div>
      {msg && <p className="text-xs font-mono mb-4 text-ash">{msg}</p>}
      {tab === 'briefing' && <BriefingTab setMsg={setMsg} />}
      {tab === 'creators' && <CreatorsTab setMsg={setMsg} />}
      {tab === 'sources' && <SourcesTab setMsg={setMsg} />}
    </div>
  )
}
