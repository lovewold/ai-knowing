import type {
  Article, CrawlResult, Report, ReportDetail, Source, Stats, AgentTool,
  GenerateReportRequest, GeneratedReport, DailyBriefing, DouyinCreator,
  HotspotFilters, HotspotResponse, HotspotSummary,
} from '../types'

const BASE = import.meta.env.VITE_API_URL || ''

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init)
  if (!res.ok) throw new Error(`请求失败: ${res.status}`)
  return res.json()
}

export const api = {
  getStats: () => fetchJson<Stats>('/api/stats'),
  getReports: (type?: string) =>
    fetchJson<Report[]>(type ? `/api/reports?report_type=${type}` : '/api/reports'),
  getReport: (id: number) => fetchJson<ReportDetail>(`/api/reports/${id}`),
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
