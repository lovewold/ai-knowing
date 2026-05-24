export interface ReportCitation {
  id: number
  title: string
  url: string
  snippet: string
  source_type: 'web' | 'article'
  article_id?: number | null
}

export interface Report {
  id: number
  title: string
  type: 'trend' | 'tool' | 'scenario' | 'agent_survey' | 'custom' | 'daily_briefing' | 'knowledge'
  quality_label: string
  created_at: string
  article_url: string | null
  source_name?: string | null
  user_prompt?: string | null
  citation_count?: number
}

export interface ReportDetail extends Report {
  content_md: string
  article_title?: string | null
  citations?: ReportCitation[]
  search_queries?: string[]
  combo_id?: number | null
}

export interface GenerateReportRequest {
  prompt: string
  article_ids?: number[]
  use_web_search?: boolean
  include_db_match?: boolean
  include_agent_tools?: boolean
  combo_id?: number | null
}

export interface GeneratedReport extends ReportDetail {}

export interface Article {
  id: number
  title: string
  title_original?: string
  summary?: string | null
  summary_original?: string | null
  content?: string | null
  url: string
  source: string
  source_id?: string
  category?: string
  signal_score: number | null
  signal_status: 'high' | 'medium' | 'low' | null
  fetched_at: string
}

export interface DailyBriefingItem {
  id: number
  sort_order: number
  item_type: 'article' | 'creator'
  article_id: number | null
  title: string
  summary: string | null
  url: string
  source_name: string | null
  signal_score: number | null
  creator_focus: string | null
}

export interface DailyBriefing {
  id: number
  briefing_date: string
  title: string
  overview: string
  theme_tags: string | null
  article_count: number
  created_at: string
  items?: DailyBriefingItem[]
}

export interface DouyinCreator {
  name: string
  profile_url: string
  focus: string
  reason: string
}

export interface AgentTool {
  id: number
  name: string
  name_original?: string
  url: string
  description?: string | null
  stars?: number | null
  tool_type?: string | null
  report_id?: number | null
  article_id?: number | null
}

export interface AgentToolDetail extends AgentTool {
  knowledge_id?: number | null
}

export interface KnowledgeEntry {
  id: number
  slug: string
  kind: 'model' | 'product' | 'skill' | string
  name: string
  summary?: string | null
  content_md?: string | null
  external_url?: string | null
  tags?: string | null
  source_type?: string
  agent_tool_id?: number | null
  last_verified_at?: string | null
  updated_at: string
  stale?: boolean
  enabled?: boolean
}

export interface KnowledgeEntryWrite {
  slug: string
  kind: 'model' | 'product' | 'skill'
  name: string
  summary?: string | null
  content_md?: string | null
  external_url?: string | null
  tags?: string | null
  enabled?: boolean
}

export interface ModelCatalogItem {
  id: number
  slug: string
  name: string
  provider?: string | null
  company_name?: string | null
  scene?: string | null
  context_len: number
  input_price?: number | null
  output_price?: number | null
  is_free: boolean
  summary?: string | null
  has_doc: boolean
  source_url?: string | null
  doc_fetched_at?: string | null
  synced_at: string
}

export interface ModelCatalogDetail extends ModelCatalogItem {}

export interface ModelCatalogDoc {
  slug: string
  has_doc: boolean
  content_md?: string | null
  doc_fetched_at?: string | null
}

export interface ModelMarketMeta {
  total: number
  with_docs: number
  providers: [string, number][]
  scenes: [string, number][]
  source: string
}

export interface ProductCatalogGroup {
  category: string
  count: number
  items: { slug: string; name: string; kind: string; summary?: string; external_url?: string }[]
}

export interface Source {
  id: string
  name: string
  type: string
  weight: number
  language: string
  enabled: boolean
  url?: string | null
  color?: string | null
}

export interface Stats {
  reports: number
  articles: number
  high_signal: number
  agent_tools: number
  agent_articles: number
  sources: number
}

export interface CrawlResult {
  status: string
  task_id?: string
  result?: Record<string, number>
}

export interface Hotspot {
  id: number
  title: string
  title_original?: string | null
  summary?: string | null
  url: string
  source: string
  source_id: string
  category?: string
  language?: string
  signal_score: number | null
  signal_status: 'high' | 'medium' | 'low' | null
  heat_level: 'high' | 'medium' | 'low'
  cross_source_count: number
  fetched_at: string
  published_at?: string | null
  is_new: boolean
}

export interface HotspotFilters {
  hours: number
  sort: 'heat' | 'newest' | 'cross_source'
  heat_level: '' | 'high' | 'medium' | 'low'
  signal_status: '' | 'high' | 'medium' | 'low'
  category: string
  source_id: string
  only_new: boolean
  min_sources: number
  q: string
}

export interface HotspotSummary {
  hours: number
  total: number
  heat_tiers: { high: number; medium: number; low: number }
  signal_tiers?: { high: number; medium: number; low: number }
  new_count: number
  by_source: Record<string, number>
  by_category: Record<string, number>
  last_updated: string | null
}

export interface HotspotResponse {
  items: Hotspot[]
  total: number
  page: number
  limit: number
}
