import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import type { ReportDetail } from '../types'
import TypeBadge from '../components/TypeBadge'
import ReportCardSections from '../components/ReportCardSections'
import ReportLinkPanel from '../components/ReportLinkPanel'
import ReportResearchChat from '../components/ReportResearchChat'
import ReportDocSidePanel from '../components/ReportDocSidePanel'
import ResizableSplitPane from '../components/ResizableSplitPane'
import { useReportResearchChat } from '../hooks/useReportResearchChat'
import { buildReportMarkdown, downloadMarkdown, sanitizeFilename } from '../utils/download'
import { splitReportSections } from '../utils/reportSections'

function extractHeadings(md: string) {
  return md
    .split('\n')
    .filter((line) => /^#{2,3}\s/.test(line))
    .map((line) => {
      const level = line.match(/^#+/)![0].length
      const text = line.replace(/^#+\s*/, '')
      const id = text.toLowerCase().replace(/[^\w\u4e00-\u9fff\s-]/g, '').replace(/\s+/g, '-')
      return { level, text, id }
    })
}

function stripReferenceSection(md: string): string {
  return md.replace(/\n##\s*参考来源[\s\S]*$/m, '').replace(/\n##\s*参考资料[\s\S]*$/m, '').trim()
}

export default function ReportDetailPage() {
  const { id } = useParams()
  const [report, setReport] = useState<ReportDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [chatMode, setChatMode] = useState(false)
  const [docCollapsed, setDocCollapsed] = useState(false)

  const chat = useReportResearchChat(report?.id ?? 0)

  useEffect(() => {
    if (!id) return
    api.getReport(Number(id)).then(setReport).catch(() => setError(true)).finally(() => setLoading(false))
  }, [id])

  useEffect(() => {
    if (!chatMode) return
    const prev = document.querySelector('main')?.style.overflow
    const main = document.querySelector('main')
    if (main) main.style.overflow = 'hidden'
    return () => {
      if (main) main.style.overflow = prev ?? ''
    }
  }, [chatMode])

  const bodyMd = useMemo(() => (report ? stripReferenceSection(report.content_md) : ''), [report])
  const { intro, sections } = useMemo(() => splitReportSections(bodyMd), [bodyMd])
  const headings = useMemo(() => (bodyMd ? extractHeadings(bodyMd) : []), [bodyMd])
  const links = report?.citations ?? []

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-20 text-center">
        <p className="font-mono text-sm text-silver">{'\u52a0\u8f7d\u4e2d...'}</p>
      </div>
    )
  }
  if (error || !report) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-20 text-center">
        <p className="font-serif text-xl mb-4">{'\u62a5\u544a\u672a\u627e\u5230'}</p>
        <Link to="/reports" className="text-sm underline">{'\u8fd4\u56de\u5217\u8868'}</Link>
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

  const displayTitle = report.title.replace(/^\[AI行业\]\s*/, '').replace(/^\[自定义\]\s*/, '')

  function handleDownloadMd() {
    const md = buildReportMarkdown(report!.title, bodyMd, {
      createdAt: report!.created_at,
      userPrompt: report!.user_prompt,
    })
    downloadMarkdown(`${sanitizeFilename(report!.title)}.md`, md)
  }

  const chatProps = {
    reportTitle: displayTitle,
    turns: chat.turns,
    suggestions: chat.suggestions,
    loading: chat.loading,
    input: chat.input,
    turnCount: chat.turnCount,
    onInputChange: chat.setInput,
    onSend: chat.send,
  }

  if (chatMode) {
    return (
      <div className="report-chat-page">
        <ResizableSplitPane
          rightCollapsed={docCollapsed}
          onToggleRight={() => setDocCollapsed((c) => !c)}
          left={(
            <ReportResearchChat
              variant="page"
              {...chatProps}
              onExitChat={() => setChatMode(false)}
            />
          )}
          right={(
            <ReportDocSidePanel
              title={displayTitle}
              reportType={report.type}
              qualityLabel={report.quality_label}
              userPrompt={report.user_prompt}
              date={date}
              intro={intro}
              sections={sections}
              links={links}
              onCollapse={() => setDocCollapsed(true)}
            />
          )}
        />
      </div>
    )
  }

  return (
    <div className="report-page min-h-screen">
      <div className="max-w-7xl mx-auto px-6 py-8 print:py-4">
        <div className="flex items-center justify-between gap-4 mb-8 print:hidden">
          <Link to="/reports" className="text-xs font-mono text-silver hover:text-ink underline">
            {'\u2190 \u8fd4\u56de\u62a5\u544a\u5217\u8868'}
          </Link>
          <div className="flex items-center gap-2">
            <button type="button" onClick={handleDownloadMd} className="text-xs font-mono px-3 py-1.5 border border-ink hover:bg-ink hover:text-paper transition-colors">
              {'\u4e0b\u8f7d Markdown'}
            </button>
            <button type="button" onClick={() => window.print()} className="text-xs font-mono px-3 py-1.5 border border-ink hover:bg-mist transition-colors">
              {'\u6253\u5370 / PDF'}
            </button>
          </div>
        </div>

        <div className="grid xl:grid-cols-[minmax(0,1fr)_300px] gap-8 xl:gap-10 items-start">
          <article className="min-w-0">
            <header className="report-hero mb-8 pb-8 border-b-2 border-ink">
              <div className="flex items-center gap-2 mb-4 flex-wrap">
                <TypeBadge type={report.type} />
                <span className="text-[10px] font-mono border border-ink px-2 py-0.5">{report.quality_label}</span>
              </div>
              <h1 className="font-serif text-3xl md:text-[2.75rem] font-semibold leading-[1.15] tracking-tight">
                {displayTitle}
              </h1>
              {report.user_prompt && (
                <p className="mt-5 text-sm text-ash leading-relaxed report-lead">{report.user_prompt}</p>
              )}
              <div className="mt-5 flex flex-wrap gap-4 text-xs font-mono text-silver">
                <time>{date}</time>
                {sections.length > 0 && <span>{sections.length} {'\u4e2a\u677f\u5757'}</span>}
                {links.length > 0 && <span>{links.length} {'\u6761\u53c2\u8003\u94fe\u63a5'}</span>}
              </div>
            </header>

            <ReportCardSections intro={intro} sections={sections} />

            <footer className="mt-12 pt-6 border-t border-ink text-xs font-mono text-silver print:mt-8">
              {'AI \u884c\u4e1a\u62a5\u544a \u00b7 \u81ea\u52a8\u751f\u6210\u4ec5\u4f9b\u53c2\u8003 \u00b7 '}{date}
            </footer>
          </article>

          <aside className="space-y-6 xl:sticky xl:top-24 print:hidden">
            <ReportResearchChat
              variant="sidebar"
              {...chatProps}
              onEnterChat={() => setChatMode(true)}
            />

            {headings.length > 0 && (
              <nav className="border border-ink p-4 bg-paper hidden xl:block">
                <p className="text-[10px] font-mono uppercase tracking-widest text-silver mb-3">{'\u76ee\u5f55'}</p>
                <div className="space-y-2 max-h-[28vh] overflow-y-auto">
                  {headings.filter((h) => h.level === 2).map((h) => (
                    <a key={h.id + h.text} href={`#${h.id}`} className="block text-xs leading-snug hover:text-ink hover:underline text-ash">
                      {h.text}
                    </a>
                  ))}
                </div>
              </nav>
            )}

            {links.length > 0 && (
              <div className="border border-ink p-4 max-h-[40vh] overflow-y-auto hidden xl:block">
                <ReportLinkPanel links={links} compact />
              </div>
            )}
          </aside>
        </div>

        {links.length > 0 && (
          <div className="xl:hidden mt-10 border-t border-ink pt-8">
            <ReportLinkPanel links={links} />
          </div>
        )}
      </div>
    </div>
  )
}
