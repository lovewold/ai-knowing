import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'

interface Props {
  entryId: number
  entryName: string
}

export default function KnowledgeReportPanel({ entryId, entryName }: Props) {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [reportId, setReportId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function generate() {
    setLoading(true)
    setError(null)
    setReportId(null)
    try {
      const res = await api.generateKnowledgeReport(entryId, prompt.trim() || undefined)
      setReportId(res.id)
    } catch {
      setError('\u751f\u6210\u5931\u8d25\uff0c\u8bf7\u68c0\u67e5 LLM \u4e0e Tavily \u914d\u7f6e\u3002')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="border border-ink bg-mist/30 p-5 md:p-6">
      <h2 className="text-lg font-semibold mb-1">{'\u751f\u6210\u6559\u7a0b\u62a5\u544a'}</h2>
      <p className="text-sm text-ash mb-4">
        {'\u7ed3\u5408\u77e5\u8bc6\u5e93\u4e0e\u7f51\u7edc\u68c0\u7d22\uff0c\u4e3a\u300c'}{entryName}{'\u300d\u751f\u6210\u6df1\u5ea6\u62a5\u544a\u3002'}
      </p>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        rows={2}
        placeholder={'\u53ef\u9009\uff1a\u81ea\u5b9a\u4e49\u62a5\u544a\u8981\u6c42\u2026'}
        className="w-full border border-smoke px-3 py-2 text-sm mb-3"
      />
      <button
        type="button"
        onClick={generate}
        disabled={loading}
        className="line-border px-4 py-2 text-sm font-medium hover:bg-ink hover:text-paper disabled:opacity-40"
      >
        {loading ? '\u751f\u6210\u4e2d\u2026' : '\u751f\u6210\u62a5\u544a'}
      </button>
      {error && <p className="mt-3 text-xs text-red-700">{error}</p>}
      {reportId && (
        <p className="mt-3 text-sm">
          {'\u62a5\u544a\u5df2\u751f\u6210\u3002 '}
          <Link to={`/reports/${reportId}`} className="underline font-medium">
            {'\u67e5\u770b\u62a5\u544a \u2192'}
          </Link>
        </p>
      )}
    </section>
  )
}
