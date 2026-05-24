export interface ReportSection {
  id: string
  title: string
  body: string
  hasImage: boolean
  insight?: string
}

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\u4e00-\u9fff\s-]/g, '')
    .replace(/\s+/g, '-')
    .slice(0, 80) || 'section'
}

function extractInsight(body: string): string | undefined {
  const quote = body.match(/^>\s*(.+)$/m)
  if (quote) return quote[1].trim().slice(0, 120)
  const bold = body.match(/\*\*(.+?)\*\*/)
  if (bold && bold[1].length < 100) return bold[1].trim()
  return undefined
}

export function splitReportSections(md: string): { intro: string; sections: ReportSection[] } {
  const text = md.trim()
  if (!text) return { intro: '', sections: [] }

  const parts = text.split(/^##\s+/m)
  if (parts.length <= 1) {
    return {
      intro: '',
      sections: [
        {
          id: 'overview',
          title: '\u62a5\u544a\u6982\u89c8',
          body: text,
          hasImage: /!\[/.test(text),
          insight: extractInsight(text),
        },
      ],
    }
  }

  const intro = parts[0].trim()
  const sections: ReportSection[] = parts.slice(1).map((chunk, i) => {
    const nl = chunk.indexOf('\n')
    const title = (nl >= 0 ? chunk.slice(0, nl) : chunk).trim()
    const body = (nl >= 0 ? chunk.slice(nl + 1) : '').trim()
    return {
      id: slugify(title) || `section-${i + 1}`,
      title,
      body,
      hasImage: /!\[/.test(body),
      insight: extractInsight(body),
    }
  })

  return { intro, sections }
}

export function sectionAccent(index: number): string {
  const accents = ['#1a1a1a', '#2d4a3e', '#3d3a6b', '#6b4a2d', '#4a2d6b', '#2d526b']
  return accents[index % accents.length]
}
