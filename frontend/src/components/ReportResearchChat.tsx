import { useEffect, useRef } from 'react'
import ChatMarkdown from './ChatMarkdown'
import { RESEARCH_STARTERS, type ChatTurn } from '../hooks/useReportResearchChat'

export type { ChatTurn }

function isPlainTextTurn(turn: ChatTurn) {
  return turn.role === 'user' || turn.content.startsWith('\u5bf9\u8bdd\u5931\u8d25')
}

function ChatTurnBubble({ turn }: { turn: ChatTurn }) {
  const isUser = turn.role === 'user'
  return (
    <div
      className={`report-research-chat__bubble ${isUser ? 'report-research-chat__bubble--user' : 'report-research-chat__bubble--assistant'}`}
    >
      <p className="report-research-chat__role">{isUser ? '\u4f60' : '\u7814\u7a76\u5bfc\u5e08'}</p>
      {isPlainTextTurn(turn) ? (
        <div className="whitespace-pre-wrap text-sm leading-relaxed">{turn.content}</div>
      ) : (
        <ChatMarkdown content={turn.content} />
      )}
    </div>
  )
}

function scrollToBottom(el: HTMLDivElement | null) {
  if (!el) return
  el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
}

interface ChatBodyProps {
  variant: 'sidebar' | 'page'
  turns: ChatTurn[]
  suggestions: string[]
  loading: boolean
  input: string
  onInputChange: (value: string) => void
  onSend: (text: string) => void
  listRef: React.RefObject<HTMLDivElement | null>
}

function ChatBody({
  variant,
  turns,
  suggestions,
  loading,
  input,
  onInputChange,
  onSend,
  listRef,
}: ChatBodyProps) {
  const isPage = variant === 'page'

  return (
    <>
      <div
        ref={listRef}
        className={`report-research-chat__thread ${isPage ? 'report-research-chat__thread--page' : 'report-research-chat__thread--sidebar'}`}
      >
        {!turns.length && !loading && (
          <p className="text-xs text-silver leading-relaxed max-w-lg">
            {'\u53ef\u4ece\u4e0b\u65b9\u5feb\u6377\u63d0\u95ee\u5f00\u59cb\uff0c\u6216\u81ea\u7531\u8f93\u5165\u4f60\u7684\u7814\u7a76\u5174\u8da3\u4e0e\u80cc\u666f\u3002'}
          </p>
        )}
        {turns.map((t, i) => (
          <ChatTurnBubble key={i} turn={t} />
        ))}
        {loading && (
          <p className="text-xs font-mono text-silver animate-pulse">{'\u601d\u8003\u4e2d\u2026'}</p>
        )}
      </div>

      {suggestions.length > 0 && !loading && (
        <div className={`report-research-chat__suggestions${isPage ? ' report-research-chat__suggestions--page' : ''}`}>
          {suggestions.slice(0, isPage ? 4 : 3).map((s) => (
            <button key={s} type="button" onClick={() => onSend(s)} className="report-research-chat__chip">
              {s}
            </button>
          ))}
        </div>
      )}

      <form
        onSubmit={(e) => { e.preventDefault(); onSend(input) }}
        className={`report-research-chat__form ${isPage ? 'report-research-chat__form--page' : ''}`}
      >
        <textarea
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          rows={isPage ? 4 : 3}
          placeholder={'\u4f8b\uff1a\u6211\u5173\u6ce8 Agent \u843d\u5730\uff0c\u5982\u4f55\u5b9a\u4e49\u7814\u7a76\u8303\u56f4\uff1f'}
          className="report-research-chat__input"
        />
        <button type="submit" disabled={loading || !input.trim()} className="report-research-chat__submit">
          {loading ? '\u56de\u590d\u4e2d\u2026' : '\u53d1\u9001'}
        </button>
      </form>
    </>
  )
}

interface Props {
  variant: 'sidebar' | 'page'
  reportTitle: string
  turns: ChatTurn[]
  suggestions: string[]
  loading: boolean
  input: string
  turnCount: number
  onInputChange: (value: string) => void
  onSend: (text: string) => void
  onEnterChat?: () => void
  onExitChat?: () => void
}

export default function ReportResearchChat({
  variant,
  reportTitle,
  turns,
  suggestions,
  loading,
  input,
  turnCount,
  onInputChange,
  onSend,
  onEnterChat,
  onExitChat,
}: Props) {
  const listRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollToBottom(listRef.current)
  }, [turns, loading])

  function handleSend(text: string) {
    onSend(text)
  }

  function handleSidebarSend(text: string) {
    onEnterChat?.()
    onSend(text)
  }

  if (variant === 'page') {
    return (
      <section className="report-research-chat report-research-chat--page">
        <header className="report-research-chat__page-header">
          <div>
            <h1 className="text-lg font-semibold">{'\u7814\u7a76\u5bfc\u5e08'}</h1>
            <p className="text-xs text-silver mt-1 leading-relaxed">
              {'\u57fa\u4e8e\u300c'}{reportTitle}{'\u300d'}
            </p>
          </div>
          <button type="button" onClick={onExitChat} className="report-research-chat__back">
            {'\u2190 \u8fd4\u56de\u9605\u8bfb'}
          </button>
        </header>

        <ChatBody
          variant="page"
          turns={turns}
          suggestions={suggestions}
          loading={loading}
          input={input}
          onInputChange={onInputChange}
          onSend={handleSend}
          listRef={listRef}
        />
      </section>
    )
  }

  return (
    <section className="report-research-chat border border-ink bg-paper">
      <div className="p-4 border-b border-smoke bg-mist/30">
        <h2 className="text-base font-semibold">{'\u7814\u7a76\u578b AI \u5bf9\u8bdd'}</h2>
        <p className="text-xs text-ash mt-1 leading-relaxed">
          {'\u57fa\u4e8e\u300c'}{reportTitle.slice(0, 40)}{reportTitle.length > 40 ? '\u2026' : ''}{'\u300d\uff0c\u53d1\u9001\u540e\u8fdb\u5165\u4e13\u5c5e\u5bf9\u8bdd\u9875\u9762\u3002'}
        </p>
      </div>

      {turnCount > 0 && (
        <div className="px-4 py-3 border-b border-smoke bg-mist/20 flex items-center justify-between gap-2">
          <p className="text-xs text-ash">
            {turnCount} {'\u8f6e\u5bf9\u8bdd'}
            {loading ? ' \u00b7 \u56de\u590d\u4e2d\u2026' : ''}
          </p>
          <button
            type="button"
            onClick={onEnterChat}
            className="text-xs font-mono px-2.5 py-1 border border-ink hover:bg-ink hover:text-paper shrink-0"
          >
            {'\u7ee7\u7eed\u5bf9\u8bdd'}
          </button>
        </div>
      )}

      {turnCount === 0 && (
        <div className="px-4 pt-3 flex flex-wrap gap-2">
          {RESEARCH_STARTERS.slice(0, 2).map((s) => (
            <button key={s} type="button" onClick={() => handleSidebarSend(s)} className="report-research-chat__chip">
              {s}
            </button>
          ))}
        </div>
      )}

      <form
        onSubmit={(e) => { e.preventDefault(); handleSidebarSend(input) }}
        className="p-4 space-y-2"
      >
        <textarea
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          rows={3}
          placeholder={'\u4f8b\uff1a\u6211\u5173\u6ce8 Agent \u843d\u5730\uff0c\u5982\u4f55\u5b9a\u4e49\u7814\u7a76\u8303\u56f4\uff1f'}
          className="report-research-chat__input"
        />
        <button type="submit" disabled={loading || !input.trim()} className="report-research-chat__submit">
          {loading ? '\u56de\u590d\u4e2d\u2026' : '\u53d1\u9001'}
        </button>
      </form>
    </section>
  )
}
