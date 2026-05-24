export interface Report {
  id: number
  title: string
  type: 'trend' | 'tool' | 'scenario' | 'agent_survey' | 'custom' | 'daily_briefing'
  quality_label: string
  created_at: string
  article_url: string | null
  source_name?: string | null
  user_prompt?: string | null
}

export interface ReportDetail extends Report {
  content_md: string
  article_title?: string | null
}

export interface GenerateReportRequest {
  prompt: string
  article_ids?: number[]
  include_recent_articles?: number
  include_agent_tools?: boolean
  include_existing_reports?: number
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

export interface Source {
  id: string
  name: string
  type: string
  weight: number
  language: string
  enabled: boolean
  url?: string | null
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
