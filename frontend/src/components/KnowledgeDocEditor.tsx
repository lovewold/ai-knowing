import { useEffect, useState } from 'react'
import MDEditor from '@uiw/react-md-editor'
import '@uiw/react-md-editor/markdown-editor.css'
import '@uiw/react-markdown-preview/markdown.css'

interface Props {
  value: string
  onChange: (value: string) => void
  height?: number
}

export default function KnowledgeDocEditor({ value, onChange, height = 520 }: Props) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <div className="border border-smoke bg-paper p-6 text-sm text-silver font-mono">
        {'\u7f16\u8f91\u5668\u52a0\u8f7d\u4e2d...'}
      </div>
    )
  }

  return (
    <div data-color-mode="light" className="border border-ink bg-paper">
      <MDEditor
        value={value}
        onChange={(v) => onChange(v ?? '')}
        height={height}
        preview="live"
        visibleDragbar={false}
        textareaProps={{ placeholder: '\u5728\u6b64\u7f16\u8f91\u6559\u7a0b\u6587\u6863\uff08Markdown \u5bcc\u6587\u672c\uff09...' }}
      />
    </div>
  )
}
