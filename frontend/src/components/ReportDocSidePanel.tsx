import TypeBadge from './TypeBadge'
import ReportCardSections from './ReportCardSections'
import ReportLinkPanel from './ReportLinkPanel'
import type { ReportCitation } from '../types'
import type { ReportSection } from '../utils/reportSections'

interface Props {
  title: string
  reportType: string
  qualityLabel: string
  userPrompt?: string | null
  date: string
  intro: string
  sections: ReportSection[]
  links: ReportCitation[]
  onCollapse?: () => void
}

export default function ReportDocSidePanel({
  title,
  reportType,
  qualityLabel,
  userPrompt,
  date,
  intro,
  sections,
  links,
  onCollapse,
}: Props) {
  return (
    <aside className="report-doc-panel">
      <header className="report-doc-panel__header">
        <div className="flex items-start justify-between gap-2 mb-2">
          <p className="text-[10px] font-mono uppercase tracking-widest text-silver">{'\u53c2\u8003\u62a5\u544a'}</p>
          {onCollapse && (
            <button type="button" onClick={onCollapse} className="report-doc-panel__collapse" title={'\u6536\u8d77\u62a5\u544a'}>
              {'\u203a'}
            </button>
          )}
        </div>
        <div className="flex items-center gap-2 mb-3 flex-wrap">
          <TypeBadge type={reportType} />
          <span className="text-[10px] font-mono border border-ink px-2 py-0.5">{qualityLabel}</span>
        </div>
        <h2 className="font-serif text-xl font-semibold leading-snug text-ink">{title}</h2>
        {userPrompt && (
          <p className="mt-3 text-xs text-ash leading-relaxed border-l-2 border-smoke pl-3">{userPrompt}</p>
        )}
        <p className="mt-3 text-[10px] font-mono text-silver">{date}</p>
      </header>

      <div className="report-doc-panel__body">
        <ReportCardSections intro={intro} sections={sections} />
        {links.length > 0 && (
          <div className="mt-8 pt-6 border-t border-smoke">
            <ReportLinkPanel links={links} compact />
          </div>
        )}
      </div>
    </aside>
  )
}
