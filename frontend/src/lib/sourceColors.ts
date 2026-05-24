/** Platform brand colors — fallback when API does not return color */
export const SOURCE_COLOR_MAP: Record<string, string> = {
  'weibo-hot': '#ff6498',
  'baidu-hot': '#6d90ff',
  'zhihu-hot': '#33eaff',
  'twitter-ai': '#33f092',
  'bilibili-rank': '#fb7299',
  'v2ex-hot': '#a0a0a0',
  hackernews: '#ff8844',
  'hn-show': '#ff8844',
  'github-trending-python': '#c8d2dc',
  'github-agents': '#c8d2dc',
  'github-multi-agents': '#c8d2dc',
  'github-mcp': '#c8d2dc',
  'github-agent-tools': '#c8d2dc',
  'google-news-ai': '#ea4335',
  'reddit-popular': '#ff4500',
  jiqizhixin: '#33eaff',
}

export function resolveSourceColor(sourceId?: string | null, apiColor?: string | null): string | null {
  if (apiColor && /^#[0-9a-fA-F]{6}$/.test(apiColor)) return apiColor
  if (sourceId && SOURCE_COLOR_MAP[sourceId]) return SOURCE_COLOR_MAP[sourceId]
  return null
}
