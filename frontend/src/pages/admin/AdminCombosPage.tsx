import { useEffect, useState, type FormEvent } from 'react'
import { adminApi, type AgentCombo, type ComboMember, type LlmModelConfig } from '../../api/admin'

export default function AdminCombosPage() {
  const [combos, setCombos] = useState<AgentCombo[]>([])
  const [models, setModels] = useState<LlmModelConfig[]>([])
  const [tools, setTools] = useState<{ id: number; name: string }[]>([])
  const [editing, setEditing] = useState<AgentCombo | null>(null)
  const [form, setForm] = useState({
    name: '',
    description: '',
    workflow_type: 'sequential',
    llm_model_id: null as number | null,
    system_prompt: '',
    enabled: true,
    members: [] as ComboMember[],
  })
  const [msg, setMsg] = useState<string | null>(null)

  function load() {
    Promise.all([adminApi.getCombos(), adminApi.getModels(), adminApi.getTools()])
      .then(([c, m, t]) => { setCombos(c); setModels(m); setTools(t) })
      .catch(() => setMsg('加载失败'))
  }

  useEffect(() => { load() }, [])

  function addMember() {
    setForm({
      ...form,
      members: [...form.members, { agent_tool_id: null, role_name: '', role_description: '', sort_order: form.members.length }],
    })
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    try {
      if (editing) {
        await adminApi.updateCombo(editing.id, form)
      } else {
        await adminApi.createCombo(form)
      }
      setForm({ name: '', description: '', workflow_type: 'sequential', llm_model_id: null, system_prompt: '', enabled: true, members: [] })
      setEditing(null)
      setMsg('已保存')
      load()
    } catch {
      setMsg('保存失败')
    }
  }

  function startEdit(c: AgentCombo) {
    setEditing(c)
    setForm({
      name: c.name,
      description: c.description || '',
      workflow_type: c.workflow_type,
      llm_model_id: c.llm_model_id,
      system_prompt: c.system_prompt || '',
      enabled: c.enabled,
      members: c.members.map((m) => ({ ...m })),
    })
  }

  return (
    <div className="p-8 max-w-3xl">
      <h1 className="font-serif text-2xl font-semibold mb-6">Agent 组合</h1>
      <p className="text-sm text-ash mb-6">定义多 Agent 工具协作方案，绑定 LLM 模型与角色分工</p>
      {msg && <p className="text-xs font-mono mb-4 text-ash">{msg}</p>}

      <form onSubmit={handleSubmit} className="border border-ink p-6 mb-8 space-y-4">
        <input className="w-full border border-smoke px-3 py-2 text-sm" placeholder="组合名称" value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        <textarea className="w-full border border-smoke px-3 py-2 text-sm" rows={2} placeholder="描述"
          value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        <div className="grid grid-cols-2 gap-4">
          <select className="border border-smoke px-2 py-2 text-sm" value={form.workflow_type}
            onChange={(e) => setForm({ ...form, workflow_type: e.target.value })}>
            <option value="sequential">sequential 顺序</option>
            <option value="parallel">parallel 并行</option>
            <option value="router">router 路由</option>
          </select>
          <select className="border border-smoke px-2 py-2 text-sm" value={form.llm_model_id ?? ''}
            onChange={(e) => setForm({ ...form, llm_model_id: e.target.value ? Number(e.target.value) : null })}>
            <option value="">默认 LLM</option>
            {models.map((m) => <option key={m.id} value={m.id}>{m.name}</option>)}
          </select>
        </div>
        <textarea className="w-full border border-smoke px-3 py-2 text-sm font-mono" rows={2} placeholder="System Prompt / 编排说明"
          value={form.system_prompt} onChange={(e) => setForm({ ...form, system_prompt: e.target.value })} />

        <div>
          <p className="text-xs font-mono text-silver mb-2">成员角色</p>
          {form.members.map((mem, i) => (
            <div key={i} className="grid grid-cols-3 gap-2 mb-2">
              <select className="border border-smoke px-2 py-1 text-xs" value={mem.agent_tool_id ?? ''}
                onChange={(e) => {
                  const members = [...form.members]
                  members[i] = { ...mem, agent_tool_id: e.target.value ? Number(e.target.value) : null }
                  setForm({ ...form, members })
                }}>
                <option value="">选择工具</option>
                {tools.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
              </select>
              <input className="border border-smoke px-2 py-1 text-xs" placeholder="角色名" value={mem.role_name}
                onChange={(e) => {
                  const members = [...form.members]
                  members[i] = { ...mem, role_name: e.target.value }
                  setForm({ ...form, members })
                }} />
              <input className="border border-smoke px-2 py-1 text-xs" placeholder="职责描述" value={mem.role_description || ''}
                onChange={(e) => {
                  const members = [...form.members]
                  members[i] = { ...mem, role_description: e.target.value }
                  setForm({ ...form, members })
                }} />
            </div>
          ))}
          <button type="button" onClick={addMember} className="text-xs underline mt-1">+ 添加成员</button>
        </div>

        <div className="flex gap-2">
          <button type="submit" className="px-4 py-2 border border-ink text-sm hover:bg-ink hover:text-paper">
            {editing ? '更新组合' : '创建组合'}
          </button>
          {editing && (
            <button type="button" onClick={() => { setEditing(null); setForm({ name: '', description: '', workflow_type: 'sequential', llm_model_id: null, system_prompt: '', enabled: true, members: [] }) }}
              className="text-sm text-ash">取消</button>
          )}
        </div>
      </form>

      <div className="border border-ink divide-y divide-smoke">
        {combos.map((c) => (
          <div key={c.id} className="p-4">
            <div className="flex justify-between">
              <div>
                <p className="font-medium">{c.name} <span className="text-xs font-mono text-silver ml-2">{c.workflow_type}</span></p>
                <p className="text-xs text-ash mt-1">{c.description}</p>
                <p className="text-xs font-mono text-silver mt-2">
                  LLM: {c.llm_model_name || '默认'} · {c.members.length} 成员
                </p>
              </div>
              <button type="button" onClick={() => startEdit(c)} className="text-xs underline shrink-0">编辑</button>
            </div>
            <ul className="mt-2 text-xs text-ash space-y-1">
              {c.members.map((m) => (
                <li key={m.id}>· {m.role_name}: {m.tool_name || '未绑定工具'} — {m.role_description}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  )
}
