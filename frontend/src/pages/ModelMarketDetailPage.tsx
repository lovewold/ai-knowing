import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import type { ModelCatalogDetail } from '../types'
import ReportMarkdown from '../components/ReportMarkdown'

export default function ModelMarketDetailPage() {
  const { slug } = useParams()
  const [model, setModel] = useState<ModelCatalogDetail | null>(null)
  const [contentMd, setContentMd] = useState<string | null>(null)
  const [metaLoading, setMetaLoading] = useState(true)
  const [docLoading, setDocLoading] = useState(false)
  const [docError, setDocError] = useState(false)

  useEffect(() => {
    if (!slug) return
    setMetaLoading(true)
    setModel(null)
    setContentMd(null)
    setDocError(false)
    api.getModelMarketDetail(slug)
      .then(setModel)
      .catch(() => setModel(null))
      .finally(() => setMetaLoading(false))
  }, [slug])

  useEffect(() => {
    if (!slug || metaLoading || !model) return
    setDocLoading(true)
    api.getModelMarketDoc(slug)
      .then((doc) => setContentMd(doc.content_md || null))
      .catch(() => setDocError(true))
      .finally(() => setDocLoading(false))
  }, [slug, model, metaLoading])

  if (metaLoading) return <p className="p-10 text-sm text-silver font-mono">{'\u52a0\u8f7d\u4e2d...'}</p>
  if (!model) return <p className="p-10 text-sm">{'\u6a21\u578b\u4e0d\u5b58\u5728'}</p>

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <Link to="/models" className="text-xs font-mono text-ash hover:text-ink underline">{'\u2190 \u6a21\u578b\u5e7f\u573a'}</Link>
      <header className="mt-4 mb-8 pb-6 border-b border-ink">
        <div className="flex flex-wrap items-center gap-2 text-[10px] font-mono text-silver uppercase">
          <span>{model.provider || model.company_name}</span>
          <span>{model.scene}</span>
          {model.is_free && <span className="text-green-800">{'\u514d\u8d39'}</span>}
        </div>
        <h1 className="text-3xl font-semibold mt-3">{model.name}</h1>
        <div className="mt-4 grid sm:grid-cols-2 gap-3 text-sm font-mono">
          <p>{'\u8f93\u5165 \u00a5'}{model.input_price ?? '-'}{' / \u767e\u4e07 tokens'}</p>
          <p>{'\u8f93\u51fa \u00a5'}{model.output_price ?? '-'}{' / \u767e\u4e07 tokens'}</p>
          {model.context_len > 0 && <p>{'\u4e0a\u4e0b\u6587\u957f\u5ea6 '}{model.context_len.toLocaleString()}</p>}
        </div>
        {model.source_url && (
          <a href={model.source_url} target="_blank" rel="noopener noreferrer" className="inline-block mt-4 text-sm underline">
            {'AGICTO \u539f\u59cb\u9875 \u2197'}
          </a>
        )}
      </header>
      {docLoading ? (
        <div className="border border-smoke p-6 bg-mist/20 animate-pulse space-y-3">
          <div className="h-4 bg-smoke/60 w-3/4" />
          <div className="h-4 bg-smoke/60 w-full" />
          <div className="h-4 bg-smoke/60 w-5/6" />
          <p className="text-xs font-mono text-silver pt-2">{'\u6587\u6863\u52a0\u8f7d\u4e2d...'}</p>
        </div>
      ) : contentMd ? (
        <article className="prose-report border border-smoke p-6 bg-paper">
          <ReportMarkdown content={contentMd} />
        </article>
      ) : (
        <p className="text-sm text-ash border border-smoke p-6">
          {docError
            ? '\u6587\u6863\u52a0\u8f7d\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5\u6216\u5728\u7ba1\u7406\u540e\u53f0\u6267\u884c\u300c\u540c\u6b65\u6a21\u578b\u5e7f\u573a\u300d\u62c9\u53d6\u6587\u6863\u3002'
            : '\u6587\u6863\u5c1a\u672a\u540c\u6b65\uff0c\u8bf7\u5728\u7ba1\u7406\u540e\u53f0\u6267\u884c\u300c\u540c\u6b65\u6a21\u578b\u5e7f\u573a\u300d\u5e76\u52fe\u9009\u62c9\u53d6\u6587\u6863\u3002'}
        </p>
      )}
    </div>
  )
}
