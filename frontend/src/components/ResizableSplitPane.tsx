import { useCallback, useEffect, useRef, useState } from 'react'

const WIDTH_KEY = 'aiknow_report_chat_doc_width'

interface Props {
  left: React.ReactNode
  right: React.ReactNode
  rightCollapsed: boolean
  onToggleRight: () => void
  defaultRightPct?: number
  minLeftPx?: number
  minRightPx?: number
}

export default function ResizableSplitPane({
  left,
  right,
  rightCollapsed,
  onToggleRight,
  defaultRightPct = 42,
  minLeftPx = 320,
  minRightPx = 280,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const dragging = useRef(false)
  const [rightPct, setRightPct] = useState(() => {
    const saved = localStorage.getItem(WIDTH_KEY)
    if (saved) {
      const n = Number(saved)
      if (n >= 24 && n <= 68) return n
    }
    return defaultRightPct
  })

  const persistWidth = useCallback((pct: number) => {
    localStorage.setItem(WIDTH_KEY, String(Math.round(pct)))
  }, [])

  useEffect(() => {
    function onMove(e: MouseEvent) {
      if (!dragging.current || !containerRef.current) return
      const rect = containerRef.current.getBoundingClientRect()
      const rightPx = rect.right - e.clientX
      const maxRight = rect.width - minLeftPx - 12
      const clamped = Math.max(minRightPx, Math.min(maxRight, rightPx))
      const pct = (clamped / rect.width) * 100
      setRightPct(pct)
    }

    function onUp() {
      if (!dragging.current) return
      dragging.current = false
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
      setRightPct((pct) => {
        persistWidth(pct)
        return pct
      })
    }

    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
    return () => {
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
    }
  }, [minLeftPx, minRightPx, persistWidth])

  function startDrag(e: React.MouseEvent) {
    e.preventDefault()
    dragging.current = true
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
  }

  return (
    <div ref={containerRef} className="resizable-split-pane">
      <div className="resizable-split-pane__left">{left}</div>

      {!rightCollapsed && (
        <>
          <button
            type="button"
            className="resizable-split-pane__handle"
            aria-label={'\u62d6\u62fd\u8c03\u6574\u5bbd\u5ea6'}
            onMouseDown={startDrag}
          />
          <div className="resizable-split-pane__right" style={{ width: `${rightPct}%` }}>
            {right}
          </div>
        </>
      )}

      {rightCollapsed && (
        <button
          type="button"
          className="resizable-split-pane__toggle resizable-split-pane__toggle--collapsed"
          onClick={onToggleRight}
          aria-label={'\u5c55\u5f00\u62a5\u544a'}
          title={'\u5c55\u5f00\u62a5\u544a'}
        >
          {'\u2039'}
        </button>
      )}
    </div>
  )
}
