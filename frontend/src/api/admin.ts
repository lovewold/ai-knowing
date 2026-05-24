const ADMIN_TOKEN_KEY = 'aiknow_admin_token'

export function getAdminToken(): string {
  return localStorage.getItem(ADMIN_TOKEN_KEY) || ''
}

export function setAdminToken(token: string) {
  localStorage.setItem(ADMIN_TOKEN_KEY, token)
}

async function adminFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const BASE = import.meta.env.VITE_API_URL || ''
  const token = getAdminToken()
  const headers: Record<string, string> = {
    ...(init?.headers as Record<string, string> | undefined),
  }
  if (token) headers['X-Admin-Token'] = token
  const res = await fetch(`${BASE}${path}`, { ...init, headers })
  if (res.status === 401) throw new Error('UNAUTHORIZED')
  if (!res.ok) throw new Error(`请求失败: ${res.status}`)
  return res.json()
}

export interface AdminStats {
  articles: number
  reports: number
  high_signal: number
  agent_tools: number
  briefings: number
  llm_models: number
  agent_combos: number
  sources: number
}

export interface LlmModelConfig {
  id: number
  name: string
  provider: string
  model_id: string
  base_url: string | null
  api_key: string | null
  has_api_key: boolean
  is_default: boolean
  enabled: boolean
  task_tags: string
  max_tokens: number
  temperature: number
}

export interface ComboMember {
  id?: number
  agent_tool_id: number | null
  tool_name?: string | null
  role_name: string
  role_description: string | null
  sort_order: number
}

export interface AgentCombo {
  id: number
  name: string
  description: string | null
  workflow_type: string
  llm_model_id: number | null
  llm_model_name: string | null
  system_prompt: string | null
  enabled: boolean
  members: ComboMember[]
}

export interface SourceConfig {
  id: string
  name: string
  type: string
  weight: number
  language: string
  enabled: boolean
  url?: string | null
  category?: string | null
  filter?: string | null
  query?: string | null
  color?: string | null
  parser?: string | null
  min_engagement?: number | null
}

export interface BriefingConfig {
  window_hours: number
  max_articles: number
  min_score: number
  include_high_signal: boolean
  include_medium_zh: boolean
  medium_zh_min_score: number
  prefer_localized: boolean
  overview_max_tokens: number
}

export interface DouyinCreator {
  name: string
  profile_url: string
  focus: string
  reason: string
}

export const adminApi = {
  getStats: () => adminFetch<AdminStats>('/api/admin/stats'),
  getModels: () => adminFetch<LlmModelConfig[]>('/api/admin/models'),
  createModel: (body: Partial<LlmModelConfig> & { name: string; provider: string; model_id: string }) =>
    adminFetch<LlmModelConfig>('/api/admin/models', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  updateModel: (id: number, body: Partial<LlmModelConfig>) =>
    adminFetch<LlmModelConfig>(`/api/admin/models/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  deleteModel: (id: number) =>
    adminFetch<{ ok: boolean }>(`/api/admin/models/${id}`, { method: 'DELETE' }),
  getCombos: () => adminFetch<AgentCombo[]>('/api/admin/agent-combos'),
  createCombo: (body: object) =>
    adminFetch<AgentCombo>('/api/admin/agent-combos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  updateCombo: (id: number, body: object) =>
    adminFetch<AgentCombo>(`/api/admin/agent-combos/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  deleteCombo: (id: number) =>
    adminFetch<{ ok: boolean }>(`/api/admin/agent-combos/${id}`, { method: 'DELETE' }),
  getSources: () => adminFetch<SourceConfig[]>('/api/admin/config/sources'),
  saveSources: (sources: SourceConfig[]) =>
    adminFetch<{ ok: boolean }>('/api/admin/config/sources', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(sources),
    }),
  getBriefingConfig: () => adminFetch<BriefingConfig>('/api/admin/config/daily-briefing'),
  saveBriefingConfig: (config: BriefingConfig) =>
    adminFetch<{ ok: boolean }>('/api/admin/config/daily-briefing', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    }),
  getCreators: () => adminFetch<DouyinCreator[]>('/api/admin/config/douyin-creators'),
  saveCreators: (creators: DouyinCreator[]) =>
    adminFetch<{ ok: boolean }>('/api/admin/config/douyin-creators', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(creators),
    }),
  getTools: () => adminFetch<{ id: number; name: string; tool_type: string | null; url: string }[]>('/api/admin/tools'),
}
