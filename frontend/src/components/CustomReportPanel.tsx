import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import ArticleDiscussPicker from './ArticleDiscussPicker'

const PRESETS = [
  '对比 LangChain、CrewAI、AutoGen 三大 Agent 框架，给出企业选型决策树',
  '分析 OpenAI、Anthropic、Google 最新 Agent 产品动向与竞争格局',
  '针对 RAG + Agent 技术栈，写一份 2026 年 AI 技术白皮书式深度综述',
  '调研 MCP 协议生态现状，评估对企业工具集成的价值',
  '撰写企业引入 AI Agent 工作流的可行性与落地路线图',
]

export default function CustomReportPanel() {
  const navigate = useNavigate()
  const [prompt, setPrompt] = useState('')
  const [selectedArticleIds, setSelectedArticleIds] = useState<number[]>([])
  const [includeDbMatch, setIncludeDbMatch] = useState(false)
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
        use_web_search: true,
        include_db_match: includeDbMatch || selectedArticleIds.length === 0,
        article_ids: selectedArticleIds.length > 0 ? selectedArticleIds : undefined,
      })
      navigate(`/reports/${report.id}`)
    } catch {
      setError('生成失败，请检查后端服务、DeepSeek 与 Tavily API 配置')
    } finally {
      setGenerating(false)
    }
  }

  return (
    <section className="mb-12 border border-ink bg-paper">
      <div className="px-6 py-5 border-b border-ink bg-mist">
        <h2 className="font-serif text-xl font-semibold">AI 行业报告</h2>
        <p className="mt-1 text-sm text-ash">聚焦大模型、Agent、RAG、AI 工具与产业动态</p>
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-4">
        <div>
          <label htmlFor="report-prompt" className="block text-xs font-mono text-silver uppercase tracking-wider mb-2">
            报告主题
          </label>
          <textarea
            id="report-prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={4}
            placeholder="例如：2026 年 AI Agent 创业赛道分析，包含技术趋势、头部玩家与落地机会..."
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
        {selectedArticleIds.length === 0 && (
          <label className="flex items-center gap-2 text-sm text-ash cursor-pointer">
            <input
              type="checkbox"
              checked={includeDbMatch}
              onChange={(e) => setIncludeDbMatch(e.target.checked)}
              className="accent-ink"
              disabled={generating}
            />
            自动匹配相关 AI 资讯
          </label>
        )}
        {error && <p className="text-xs text-red-700 font-mono">{error}</p>}
        <button
          type="submit"
          disabled={generating}
          className="line-border px-6 py-2.5 text-sm font-medium hover:bg-ink hover:text-paper disabled:opacity-40 transition-colors"
        >
          {generating ? '正在生成 AI 行业报告…' : '生成报告'}
        </button>
      </form>

      <ArticleDiscussPicker
        selectedIds={selectedArticleIds}
        onChange={setSelectedArticleIds}
        disabled={generating}
      />
    </section>
  )
}
