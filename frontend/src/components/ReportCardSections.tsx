import ReportMarkdown from './ReportMarkdown'
import type { ReportSection } from '../utils/reportSections'
import { sectionAccent } from '../utils/reportSections'

interface Props {
  intro: string
  sections: ReportSection[]
}

export default function ReportCardSections({ intro, sections }: Props) {
  return (
    <div className="report-cards space-y-6">
      {intro && (
        <section className="report-section-card report-section-card--lead">
          <div className="report-section-card__visual" aria-hidden>
            <span className="report-section-card__glyph">{'\u2726'}</span>
          </div>
          <div className="report-section-card__content">
            <p className="text-[10px] font-mono uppercase tracking-widest text-silver mb-2">{'\u6458\u8981'}</p>
            <div className="prose-report prose-report-inset">
              <ReportMarkdown content={intro} />
            </div>
          </div>
        </section>
      )}

      {sections.map((sec, i) => (
        <section
          key={sec.id + i}
          id={sec.id}
          className="report-section-card scroll-mt-28"
          style={{ '--card-accent': sectionAccent(i) } as React.CSSProperties}
        >
          <div className="report-section-card__header">
            <div className="report-section-card__index-wrap">
              <span className="report-section-card__index">{String(i + 1).padStart(2, '0')}</span>
              {sec.hasImage && <span className="report-section-card__badge">{'\u56fe\u6587'}</span>}
            </div>
            <h2 className="report-section-card__title">{sec.title}</h2>
            {sec.insight && (
              <p className="report-section-card__insight">{sec.insight}</p>
            )}
          </div>
          <div className="report-section-card__body prose-report prose-report-inset">
            <ReportMarkdown content={sec.body} />
          </div>
        </section>
      ))}
    </div>
  )
}
