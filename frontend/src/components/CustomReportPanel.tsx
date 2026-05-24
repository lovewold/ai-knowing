import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'

const PRESETS = [
  '总结最近高信号 AI 资讯，提炼本周五大趋势与关注建议',
  '对比 LangChain、CrewAI、AutoGen 三大 Agent 框架，给出企业选型决策树',
  '撰写一份「企业引入 AI Agent 工作流」可行性分析与落地路线图',
  '基于当前 Agent 工具库，生成竞品矩阵与差异化机会分析',
  '针对 RAG + Agent 技术栈，写一份技术白皮书式深度综述',
]

export default function CustomReportPanel() {
  const navigate = useNavigate()
  const [prompt, setPrompt] = useState('')
  const [includeArticles, setIncludeArticles] = useState(true)
  const [includeTools, setIncludeTools] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (prompt.trim().length < 5) {
      setError('请至少输入 5 个字的报告描述')
      return
    }
    setGenerating(true)
    setError(null)
    try {
      const report = await api.generateCustomReport({
        prompt: prompt.trim(),
        include_recent_articles: includeArticles ? 15 : 0,
        include_agent_tools: includeTools,
        include_existing_reports: 2,
      })
      navigate(`/reports/${report.id}`)
    } catch {
      setError('生成失败，请检查后端服务与 DeepSeek API 配置')
    } finally {
      setGenerating(false)
    }
  }

  return (
    <section className="mb-12 border border-ink bg-paper">
      <div className="px-6 py-5 border-b border-ink bg-mist">
        <h2 className="font-serif text-xl font-semibold">自定义报告</h2>
        <p className="mt-1 text-sm text-ash">
          用自然语言描述你想要的报告类型、分析角度与结构，AI 将结合知识库数据生成
        </p>
      </div>
      <form onSubmit={handleSubmit} className="p-6 space-y-4">
        <div>
          <label htmlFor="report-prompt" className="block text-xs font-mono text-silver uppercase tracking-wider mb-2">
            报告描述
          </label>
          <textarea
            id="report-prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={4}
            placeholder="例如：写一份 2026 年 AI Agent 创业赛道投资分析，包含市场规模、头部玩家、风险与机会..."
            className="w-full border border-ink px-4 py-3 text-sm leading-relaxed resize-y min-h-[120px] focus:outline-none focus:ring-1 focus:ring-ink bg-paper"
            disabled={generating}
          />
        </div>
        <div className="flex flex-wrap gap-2">
          {PRESETS.map((preset) => (
            <button
              key={preset}
              type="button"
              onClick={() => setPrompt(preset)}
              className="text-xs px-3 py-1.5 border border-smoke text-ash hover:border-ink hover:text-ink hover:bg-mist transition-colors text-left max-w-full truncate"
              title={preset}
            >
              {preset.length > 36 ? `${preset.slice(0, 36)}…` : preset}
            </button>
          ))}
        </div>
        <div className="flex flex-wrap gap-6 text-sm text-ash">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={includeArticles}
              onChange={(e) => setIncludeArticles(e.target.checked)}
              className="accent-ink"
              disabled={generating}
            />
            附带最近资讯（15 条）
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={includeTools}
              onChange={(e) => setIncludeTools(e.target.checked)}
              className="accent-ink"
              disabled={generating}
            />
            附带 Agent 工具库
          </label>
        </div>
        {error && <p className="text-xs text-red-700 font-mono">{error}</p>}
        <button
          type="submit"
          disabled={generating}
          className="line-border px-6 py-2.5 text-sm font-medium hover:bg-ink hover:text-paper disabled:opacity-40 transition-colors"
        >
          {generating ? '正在生成报告…' : '生成自定义报告'}
        </button>
      </form>
    </section>
  )
}
