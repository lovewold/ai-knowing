import { useCallback, useState } from 'react'
import { api } from '../api/client'

export interface ChatTurn {
  role: 'user' | 'assistant'
  content: string
}

export const RESEARCH_STARTERS = [
  '\u5e2e\u6211\u63d0\u70bc 3 \u4e2a\u53ef\u6df1\u5165\u7684\u7814\u7a76\u95ee\u9898',
  '\u5982\u679c\u6211\u662f\u521d\u5b66\u8005\uff0c\u5e94\u4ece\u54ea\u91cc\u5f00\u59cb\uff1f',
  '\u8fd9\u4e2a\u65b9\u5411\u6709\u54ea\u4e9b\u6f5c\u5728\u98ce\u9669\uff1f',
  '\u63a8\u8350\u5177\u4f53\u7684\u9a8c\u8bc1\u8def\u5f84\u6216\u5c0f\u5b9e\u9a8c',
]

export function useReportResearchChat(reportId: number) {
  const [input, setInput] = useState('')
  const [turns, setTurns] = useState<ChatTurn[]>([])
  const [suggestions, setSuggestions] = useState<string[]>(RESEARCH_STARTERS)
  const [loading, setLoading] = useState(false)

  const send = useCallback(async (text: string) => {
    const msg = text.trim()
    if (!msg || loading) return

    setInput('')
    const history = turns
    const userTurn: ChatTurn = { role: 'user', content: msg }
    setTurns((prev) => [...prev, userTurn])
    setLoading(true)

    try {
      const res = await api.discussReport(reportId, msg, history)
      setTurns((prev) => [...prev, { role: 'assistant', content: res.reply }])
      setSuggestions(res.suggestions?.length ? res.suggestions : RESEARCH_STARTERS)
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : '\u5bf9\u8bdd\u5931\u8d25'
      setTurns((prev) => [...prev, { role: 'assistant', content: `\u5bf9\u8bdd\u5931\u8d25\uff1a${errMsg}` }])
    } finally {
      setLoading(false)
    }
  }, [reportId, loading, turns])

  const turnCount = turns.filter((t) => t.role === 'user').length

  return {
    input,
    setInput,
    turns,
    suggestions,
    loading,
    send,
    turnCount,
  }
}
