import type {
  Article, CrawlResult, Report, ReportDetail, Source, Stats, AgentTool, AgentToolDetail,
  GenerateReportRequest, GeneratedReport, DailyBriefing, DouyinCreator,
  HotspotFilters, HotspotResponse, HotspotSummary, KnowledgeEntry, KnowledgeEntryWrite,
  ModelCatalogDetail, ModelCatalogDoc, ModelCatalogItem, ModelMarketMeta, ProductCatalogGroup,
} from '../types'

const BASE = import.meta.env.VITE_API_URL || ''

const modelDocCache = {
  _map: new Map<string, Promise<ModelCatalogDoc>>(),
  get(slug: string) {
    let p = this._map.get(slug)
    if (!p) {
      p = fetchJson<ModelCatalogDoc>(`/api/marketplace/models/${encodeURIComponent(slug)}/doc`)
      this._map.set(slug, p)
    }
    return p
  },
  prefetch(slug: string) {
    if (!this._map.has(slug)) this.get(slug)
  },
  clear(slug?: string) {
    if (slug) this._map.delete(slug)
    else this._map.clear()
  },
}

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init)
  if (!res.ok) {
    let detail = `HTTP ${res.status}`
    try {
      const body = await res.json()
      if (body?.detail) {
        detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
      }
    } catch {
      /* ignore */
    }
    throw new Error(detail)
  }
  return res.json()
}

export const api = {
  getStats: () => fetchJson<Stats>('/api/stats'),
  getReports: (type?: string) =>
    fetchJson<Report[]>(type ? `/api/reports?report_type=${type}` : '/api/reports'),
  getReport: (id: number) => fetchJson<ReportDetail>(`/api/reports/${id}`),
  discussReport: (id: number, message: string, history: { role: string; content: string }[]) =>
    fetchJson<{ reply: string; suggestions: string[] }>(`/api/reports/${id}/discuss`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history }),
    }),
  getArticles: (category?: string, minScore?: number) => {
    const params = new URLSearchParams()
    if (category) params.set('category', category)
    if (minScore != null) params.set('min_score', String(minScore))
    params.set('sort', 'score')
    const q = params.toString()
    return fetchJson<Article[]>(q ? `/api/articles?${q}` : '/api/articles?sort=score')
  },
  getArticle: (id: number) => fetchJson<Article>(`/api/articles/${id}`),
  getDailyBriefings: () => fetchJson<DailyBriefing[]>('/api/daily-briefings'),
  getLatestDailyBriefing: () => fetchJson<DailyBriefing>('/api/daily-briefings/latest'),
  getDailyBriefing: (id: number) => fetchJson<DailyBriefing>(`/api/daily-briefings/${id}`),
  generateDailyBriefing: () =>
    fetchJson<DailyBriefing>('/api/daily-briefings/generate', { method: 'POST' }),
  getDouyinCreators: () => fetchJson<DouyinCreator[]>('/api/creators/douyin'),
  getAgentTools: () => fetchJson<AgentTool[]>('/api/agent-tools'),
  getAgentTool: (id: number) => fetchJson<AgentToolDetail>(`/api/agent-tools/${id}`),
  getKnowledgeList: (kind?: string, q?: string, category?: string) => {
    const p = new URLSearchParams()
    if (kind) p.set('kind', kind)
    if (q) p.set('q', q)
    if (category) p.set('category', category)
    const qs = p.toString()
    return fetchJson<KnowledgeEntry[]>(qs ? `/api/knowledge?${qs}` : '/api/knowledge')
  },
  getKnowledgeAdminList: (opts: { kind?: string; q?: string } = {}) => {
    const p = new URLSearchParams({ admin: 'true' })
    if (opts.kind) p.set('kind', opts.kind)
    if (opts.q) p.set('q', opts.q)
    return fetchJson<KnowledgeEntry[]>(`/api/knowledge?${p.toString()}`)
  },
  getProductCatalog: () => fetchJson<{ groups: ProductCatalogGroup[]; total: number }>('/api/knowledge/catalog'),
  generateKnowledgeDocs: (limit = 50, force = false) =>
    fetchJson<{ processed: number; updated: number; failed: number }>(
      `/api/knowledge/generate-docs?limit=${limit}&force=${force}`,
      { method: 'POST' },
    ),
  getModelMarketMeta: () => fetchJson<ModelMarketMeta>('/api/marketplace/meta'),
  getModelMarketList: (opts: { provider?: string; scene?: string; q?: string; free?: boolean; limit?: number; offset?: number } = {}) => {
    const p = new URLSearchParams()
    if (opts.provider) p.set('provider', opts.provider)
    if (opts.scene) p.set('scene', opts.scene)
    if (opts.q) p.set('q', opts.q)
    if (opts.free === true) p.set('free', 'true')
    if (opts.free === false) p.set('free', 'false')
    if (opts.limit) p.set('limit', String(opts.limit))
    if (opts.offset) p.set('offset', String(opts.offset))
    const qs = p.toString()
    return fetchJson<{ items: ModelCatalogItem[]; total: number }>(qs ? `/api/marketplace/models?${qs}` : '/api/marketplace/models')
  },
  getModelMarketDetail: (slug: string) => fetchJson<ModelCatalogDetail>(`/api/marketplace/models/${encodeURIComponent(slug)}`),
  getModelMarketDoc: (slug: string) => modelDocCache.get(slug),
  prefetchModelMarketDoc: (slug: string) => {
    modelDocCache.prefetch(slug)
  },
  syncModelMarket: (fetchDocs = true, docLimit = 40) =>
    fetchJson<{ list_count: number; created: number; total: number; docs_fetched: number }>(
      `/api/marketplace/sync?fetch_docs=${fetchDocs}&doc_limit=${docLimit}`,
      { method: 'POST' },
    ),
  getKnowledge: (id: number) => fetchJson<KnowledgeEntry>(`/api/knowledge/${id}`),
  getKnowledgeAdmin: (id: number) => fetchJson<KnowledgeEntry>(`/api/knowledge/${id}?admin=true`),
  createKnowledge: (body: KnowledgeEntryWrite) =>
    fetchJson<KnowledgeEntry>(`/api/knowledge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  updateKnowledge: (id: number, body: KnowledgeEntryWrite) =>
    fetchJson<KnowledgeEntry>(`/api/knowledge/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  deleteKnowledge: (id: number, hard = false) =>
    fetchJson<{ deleted: boolean; hard: boolean }>(`/api/knowledge/${id}?hard=${hard}`, { method: 'DELETE' }),
  generateKnowledgeDoc: (id: number, force = false) =>
    fetchJson<{ updated: boolean; entry: KnowledgeEntry }>(`/api/knowledge/${id}/generate-doc?force=${force}`, { method: 'POST' }),
  askKnowledge: (id: number, question: string) =>
    fetchJson<{ answer: string; context_count: number }>(`/api/knowledge/${id}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    }),
  generateKnowledgeReport: (id: number, prompt?: string) =>
    fetchJson<ReportDetail>(`/api/knowledge/${id}/report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: prompt || null }),
    }),
  getSources: () => fetchJson<Source[]>('/api/sources'),
  triggerCrawl: (asyncMode = true) =>
    fetchJson<CrawlResult>(`/api/crawl/trigger?async_mode=${asyncMode}`, { method: 'POST' }),
  backfillLocalize: (limit = 50) =>
    fetchJson<{ status: string; result: { localized: number } }>(
      `/api/localize/backfill?limit=${limit}`, { method: 'POST' },
    ),
  generateAgentSurvey: () =>
    fetchJson<{ status: string; message: string; seeded: number }>(
      '/api/agent-tools/survey', { method: 'POST' },
    ),
  generateCustomReport: (body: GenerateReportRequest) =>
    fetchJson<GeneratedReport>('/api/reports/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  downloadReportUrl: (id: number) => `${BASE}/api/reports/${id}/download`,
  getHotspots: (filters: HotspotFilters, page = 1, limit = 30) => {
    const params = new URLSearchParams()
    params.set('hours', String(filters.hours))
    params.set('sort', filters.sort)
    params.set('page', String(page))
    params.set('limit', String(limit))
    if (filters.heat_level) params.set('heat_level', filters.heat_level)
    if (filters.signal_status) params.set('signal_status', filters.signal_status)
    if (filters.category) params.set('category', filters.category)
    if (filters.source_id) params.set('source_id', filters.source_id)
    if (filters.only_new) params.set('only_new', 'true')
    if (filters.min_sources >= 2) params.set('min_sources', String(filters.min_sources))
    if (filters.q.trim()) params.set('q', filters.q.trim())
    return fetchJson<HotspotResponse>(`/api/hotspots?${params}`)
  },
  getHotspotSummary: (hours = 24) =>
    fetchJson<HotspotSummary>(`/api/hotspots/summary?hours=${hours}`),
}
