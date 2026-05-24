import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import type { ReportDetail } from '../types'
import TypeBadge from '../components/TypeBadge'
import ReportMarkdown from '../components/ReportMarkdown'
import { buildReportMarkdown, downloadMarkdown, sanitizeFilename } from '../utils/download'

function extractHeadings(md: string) {
  return md
    .split('\n')
    .filter((line) => /^#{2,3}\s/.test(line))
    .map((line) => {
      const level = line.match(/^#+/)![0].length
      const text = line.replace(/^#+\s*/, '')
      const id = text.toLowerCase().replace(/[^\w一-鿿\s-]/g, '').replace(/\s+/g, '-')
      return { level, text, id }
    })
}

export default function ReportDetailPage() {
  const { id } = useParams()
  const [report, setReport] = useState<ReportDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    if (!id) return
    api.getReport(Number(id)).then(setReport).catch(() => setError(true)).finally(() => setLoading(false))
  }, [id])

  const headings = useMemo(() => (report ? extractHeadings(report.content_md) : []), [report])

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-6 py-20 text-center">
        <p className="font-mono text-sm text-silver">加载中...</p>
      </div>
    )
  }
  if (error || !report) {
    return (
      <div className="max-w-5xl mx-auto px-6 py-20 text-center">
        <p className="font-serif text-xl mb-4">报告未找到</p>
        <Link to="/reports" className="text-sm underline">返回列表</Link>
      </div>
    )
  }

  const date = new Date(report.created_at).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

  function handleDownloadMd() {
    const md = buildReportMarkdown(report!.title, report!.content_md, {
      createdAt: report!.created_at,
      userPrompt: report!.user_prompt,
    })
    downloadMarkdown(`${sanitizeFilename(report!.title)}.md`, md)
  }

  return (
    <div className="report-page">
      <div className="max-w-5xl mx-auto px-6 py-8 print:py-4">
        <div className="flex items-center justify-between gap-4 mb-8 print:hidden">
          <Link to="/reports" className="text-xs font-mono text-silver hover:text-ink underline">
            &larr; 返回报告列表
          </Link>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleDownloadMd}
              className="text-xs font-mono px-3 py-1.5 border border-ink hover:bg-ink hover:text-paper transition-colors"
            >
              下载 Markdown
            </button>
            <button
              type="button"
              onClick={() => window.print()}
              className="text-xs font-mono px-3 py-1.5 border border-ink hover:bg-mist transition-colors"
            >
              打印 / PDF
            </button>
          </div>
        </div>

        <div className="grid lg:grid-cols-[1fr_200px] gap-10 items-start">
          <article className="min-w-0">
            <header className="report-header pb-8 mb-10 border-b-2 border-ink">
              <div className="flex items-center gap-2 mb-4 flex-wrap">
                <TypeBadge type={report.type} />
                <span className="text-[10px] font-mono border border-ink px-2 py-0.5">{report.quality_label}</span>
              </div>
              <h1 className="font-serif text-3xl md:text-[2.5rem] font-semibold leading-tight tracking-tight">
                {report.title}
              </h1>
              {report.user_prompt && (
                <p className="mt-4 text-sm text-ash leading-relaxed border-l-2 border-ink pl-4 italic">
                  {report.user_prompt}
                </p>
              )}
              <div className="mt-5 flex flex-wrap gap-4 text-xs font-mono text-silver">
                <time>{date}</time>
                {report.source_name && <span>{report.source_name}</span>}
                {report.article_url && (
                  <a href={report.article_url} target="_blank" rel="noopener noreferrer" className="underline hover:text-ink">
                    原始来源
                  </a>
                )}
              </div>
            </header>

            <ReportMarkdown content={report.content_md} />

            <footer className="mt-16 pt-6 border-t border-ink text-xs font-mono text-silver print:mt-8">
              本报告由 AI 自动生成，仅供参考。生成时间 {date}
            </footer>
          </article>

          {headings.length > 0 && (
            <aside className="hidden lg:block sticky top-24 print:hidden">
              <p className="text-[10px] font-mono uppercase tracking-widest text-silver mb-3">目录</p>
              <nav className="border border-ink p-4 space-y-2 max-h-[70vh] overflow-y-auto">
                {headings.map((h) => (
                  <a
                    key={h.id + h.text}
                    href={`#${h.id}`}
                    className={`block text-xs leading-snug hover:text-ink hover:underline underline-offset-2 text-ash ${h.level === 3 ? 'pl-3' : ''}`}
                  >
                    {h.text}
                  </a>
                ))}
              </nav>
            </aside>
          )}
        </div>
      </div>
    </div>
  )
}
