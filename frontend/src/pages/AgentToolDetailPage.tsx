import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import type { AgentToolDetail } from '../types'
import KnowledgeAskPanel from '../components/KnowledgeAskPanel'
import KnowledgeReportPanel from '../components/KnowledgeReportPanel'

export default function AgentToolDetailPage() {
  const { id } = useParams()
  const [tool, setTool] = useState<AgentToolDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    api.getAgentTool(Number(id)).then(setTool).catch(() => setTool(null)).finally(() => setLoading(false))
  }, [id])

  if (loading) return <p className="p-10 text-sm text-silver font-mono">{'\u52a0\u8f7d\u4e2d...'}</p>
  if (!tool) return <p className="p-10 text-sm">{'\u5de5\u5177\u4e0d\u5b58\u5728'}</p>

  const kid = tool.knowledge_id

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <Link to="/agents" className="text-xs font-mono text-ash hover:text-ink underline">{'\u2190 Agent \u5de5\u5177'}</Link>
      <header className="mt-4 mb-8 pb-6 border-b border-ink">
        <h1 className="text-3xl font-semibold">{tool.name}</h1>
        {tool.tool_type && <p className="text-xs font-mono text-silver mt-2">{tool.tool_type}</p>}
        {tool.description && <p className="text-base text-ash mt-4 leading-relaxed">{tool.description}</p>}
        <div className="mt-4 flex flex-wrap gap-3">
          <a href={tool.url} target="_blank" rel="noopener noreferrer" className="text-sm underline">{'\u9879\u76ee\u94fe\u63a5 \u2197'}</a>
          {kid && <Link to={`/knowledge/${kid}`} className="text-sm underline">{'\u77e5\u8bc6\u5e93\u6559\u7a0b \u2192'}</Link>}
        </div>
      </header>
      {kid ? (
        <div className="grid lg:grid-cols-2 gap-6">
          <KnowledgeAskPanel entryId={kid} entryName={tool.name} />
          <KnowledgeReportPanel entryId={kid} entryName={tool.name} />
        </div>
      ) : (
        <p className="text-sm text-ash">{'\u77e5\u8bc6\u5e93\u7d22\u5f15\u540c\u6b65\u4e2d\uff0c\u8bf7\u7a0d\u540e\u5237\u65b0\u3002'}</p>
      )}
    </div>
  )
}
