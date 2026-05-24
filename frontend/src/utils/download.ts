export function downloadMarkdown(filename: string, content: string) {
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename.endsWith('.md') ? filename : `${filename}.md`
  a.click()
  URL.revokeObjectURL(url)
}

export function sanitizeFilename(name: string) {
  return name.replace(/[<>:"/\\|?*]/g, '_').slice(0, 80)
}

export function buildReportMarkdown(
  title: string,
  content: string,
  meta?: { createdAt?: string; userPrompt?: string | null },
) {
  const lines = [`# ${title}`, '']
  if (meta?.userPrompt) lines.push(`> 用户需求: ${meta.userPrompt}`, '')
  if (meta?.createdAt) lines.push(`> 生成时间: ${meta.createdAt}`, '')
  if (meta?.userPrompt || meta?.createdAt) lines.push('')
  lines.push(content)
  return lines.join('\n')
}
