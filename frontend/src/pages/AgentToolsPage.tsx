import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import type { AgentTool } from '../types'
import EmptyState from '../components/EmptyState'

export default function AgentToolsPage() {
  const [tools, setTools] = useState<AgentTool[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [surveyMsg, setSurveyMsg] = useState<string | null>(null)

  useEffect(() => {
    api.getAgentTools().then(setTools).catch(console.error).finally(() => setLoading(false))
  }, [])

  async function handleGenerateSurvey() {
    setGenerating(true)
    setSurveyMsg('正在生成 Agent 全景调研报告...')
    try {
      const res = await api.generateAgentSurvey()
      setSurveyMsg(res.message || '报告已排队生成')
    } catch {
      setSurveyMsg('生成失败，请检查后端与 DeepSeek API')
    } finally {
      setGenerating(false)
    }
  }

  const grouped = tools.reduce<Record<string, AgentTool[]>>((acc, t) => {
    const key = t.tool_type || '其他'
    if (!acc[key]) acc[key] = []
    acc[key].push(t)
    return acc
  }, {})

  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      <header className="mb-10 pb-6 border-b border-ink">
        <h1 className="font-serif text-3xl font-semibold">Agent 工具汇总</h1>
        <p className="mt-2 text-sm text-ash">
          自动抓取 GitHub Agent 框架/工具，生成中文调研报告
        </p>
        <div className="mt-4 flex gap-3">
          <button
            onClick={handleGenerateSurvey}
            disabled={generating || tools.length === 0}
            className="line-border px-4 py-2 text-sm font-medium hover:bg-ink hover:text-paper disabled:opacity-40"
          >
            {generating ? '生成中...' : '生成全景调研报告'}
          </button>
          <Link to="/reports?type=agent_survey" className="px-4 py-2 text-sm border border-ink hover:bg-mist">
            查看 Agent 报告
          </Link>
        </div>
        {surveyMsg && <p className="mt-3 text-xs font-mono text-ash">{surveyMsg}</p>}
      </header>

      {loading ? (
        <p className="text-sm text-silver font-mono">加载中...</p>
      ) : tools.length === 0 ? (
        <EmptyState title="暂无 Agent 工具" description="点击顶部立即抓取，或等待 GitHub Agent 源采集完成" />
      ) : (
        Object.entries(grouped).map(([type, items]) => (
          <section key={type} className="mb-10">
            <h2 className="font-serif text-lg font-semibold mb-4 pb-2 border-b border-ink">
              {type} <span className="text-sm font-mono text-silver ml-2">({items.length})</span>
            </h2>
            <div className="border border-ink divide-y divide-smoke">
              {items.map((tool) => (
                <div key={tool.id} className="p-4 hover:bg-mist transition-colors">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <a
                        href={tool.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-medium hover:underline underline-offset-2"
                      >
                        {tool.name}
                      </a>
                      {tool.description && (
                        <p className="text-xs text-ash mt-1.5 leading-relaxed">{tool.description}</p>
                      )}
                    </div>
                    {tool.stars != null && (
                      <span className="font-mono text-xs text-silver shrink-0">★ {tool.stars}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        ))
      )}
    </div>
  )
}
