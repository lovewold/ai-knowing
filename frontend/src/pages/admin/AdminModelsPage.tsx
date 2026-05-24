import { useEffect, useState } from 'react'
import { adminApi, type LlmModelConfig } from '../../api/admin'

const PROVIDERS = ['deepseek', 'openai', 'anthropic', 'openai_compatible']
const TASKS = ['report', 'custom', 'briefing', 'localize', 'agent']

const emptyForm = {
  name: '',
  provider: 'deepseek',
  model_id: 'deepseek-chat',
  base_url: 'https://api.deepseek.com',
  api_key: '',
  is_default: false,
  enabled: true,
  task_tags: TASKS.join(','),
  max_tokens: 4096,
  temperature: 0.3,
}

export default function AdminModelsPage() {
  const [models, setModels] = useState<LlmModelConfig[]>([])
  const [form, setForm] = useState({ ...emptyForm })
  const [editingId, setEditingId] = useState<number | null>(null)
  const [msg, setMsg] = useState<string | null>(null)

  function load() {
    adminApi.getModels().then(setModels).catch(() => setMsg('加载失败，请检查 Token'))
  }

  useEffect(() => { load() }, [])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    try {
      if (editingId) {
        await adminApi.updateModel(editingId, form)
      } else {
        await adminApi.createModel(form)
      }
      setForm({ ...emptyForm })
      setEditingId(null)
      setMsg('已保存')
      load()
    } catch {
      setMsg('保存失败')
    }
  }

  async function handleDelete(id: number) {
    if (!confirm('确定删除此模型？')) return
    try {
      await adminApi.deleteModel(id)
      load()
    } catch {
      setMsg('删除失败（默认模型不可删）')
    }
  }

  function startEdit(m: LlmModelConfig) {
    setEditingId(m.id)
    setForm({
      name: m.name,
      provider: m.provider,
      model_id: m.model_id,
      base_url: m.base_url || '',
      api_key: '',
      is_default: m.is_default,
      enabled: m.enabled,
      task_tags: m.task_tags,
      max_tokens: m.max_tokens,
      temperature: m.temperature,
    })
  }

  return (
    <div className="p-8 max-w-3xl">
      <h1 className="font-serif text-2xl font-semibold mb-6">多模型配置</h1>
      <p className="text-sm text-ash mb-6">
        按任务标签分配模型：report / custom / briefing / localize / agent。留空 API Key 则不更新。
      </p>
      {msg && <p className="text-xs font-mono mb-4 text-ash">{msg}</p>}

      <form onSubmit={handleSubmit} className="border border-ink p-6 mb-8 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <label className="block text-xs">
            名称
            <input className="w-full border border-smoke px-2 py-1.5 mt-1 text-sm" value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          </label>
          <label className="block text-xs">
            Provider
            <select className="w-full border border-smoke px-2 py-1.5 mt-1 text-sm" value={form.provider}
              onChange={(e) => setForm({ ...form, provider: e.target.value })}>
              {PROVIDERS.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </label>
          <label className="block text-xs">
            Model ID
            <input className="w-full border border-smoke px-2 py-1.5 mt-1 text-sm" value={form.model_id}
              onChange={(e) => setForm({ ...form, model_id: e.target.value })} required />
          </label>
          <label className="block text-xs">
            Base URL
            <input className="w-full border border-smoke px-2 py-1.5 mt-1 text-sm" value={form.base_url}
              onChange={(e) => setForm({ ...form, base_url: e.target.value })} />
          </label>
          <label className="block text-xs col-span-2">
            API Key {editingId && '(留空不修改)'}
            <input type="password" className="w-full border border-smoke px-2 py-1.5 mt-1 text-sm font-mono"
              value={form.api_key} onChange={(e) => setForm({ ...form, api_key: e.target.value })} />
          </label>
          <label className="block text-xs col-span-2">
            任务标签（逗号分隔）
            <input className="w-full border border-smoke px-2 py-1.5 mt-1 text-sm font-mono" value={form.task_tags}
              onChange={(e) => setForm({ ...form, task_tags: e.target.value })} />
          </label>
        </div>
        <div className="flex gap-4 text-sm">
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={form.is_default} onChange={(e) => setForm({ ...form, is_default: e.target.checked })} />
            默认模型
          </label>
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={form.enabled} onChange={(e) => setForm({ ...form, enabled: e.target.checked })} />
            启用
          </label>
        </div>
        <div className="flex gap-2">
          <button type="submit" className="px-4 py-2 border border-ink text-sm hover:bg-ink hover:text-paper">
            {editingId ? '更新' : '添加模型'}
          </button>
          {editingId && (
            <button type="button" onClick={() => { setEditingId(null); setForm({ ...emptyForm }) }}
              className="px-4 py-2 text-sm text-ash">取消</button>
          )}
        </div>
      </form>

      <div className="border border-ink divide-y divide-smoke">
        {models.map((m) => (
          <div key={m.id} className="p-4 flex justify-between gap-4">
            <div>
              <p className="font-medium text-sm">
                {m.name} {m.is_default && <span className="text-[10px] border border-ink px-1 ml-1">默认</span>}
                {!m.enabled && <span className="text-[10px] text-silver ml-1">已禁用</span>}
              </p>
              <p className="text-xs font-mono text-silver mt-1">{m.provider} / {m.model_id}</p>
              <p className="text-xs text-ash mt-1">任务: {m.task_tags} · Key: {m.has_api_key ? '已配置' : '未配置'}</p>
            </div>
            <div className="flex gap-2 shrink-0">
              <button type="button" onClick={() => startEdit(m)} className="text-xs underline">编辑</button>
              <button type="button" onClick={() => handleDelete(m.id)} className="text-xs text-red-700 underline">删除</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
