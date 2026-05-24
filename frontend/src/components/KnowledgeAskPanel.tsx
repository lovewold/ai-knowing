import { useState } from 'react'
import { api } from '../api/client'

interface Props {
  entryId: number
  entryName: string
}

export default function KnowledgeAskPanel({ entryId, entryName }: Props) {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    if (!question.trim()) return
    setLoading(true)
    setAnswer(null)
    try {
      const res = await api.askKnowledge(entryId, question.trim())
      setAnswer(res.answer)
    } catch {
      setAnswer('\u95ee\u7b54\u5931\u8d25\uff0c\u8bf7\u68c0\u67e5\u540e\u7aef\u662f\u5426\u5df2\u542f\u52a8\u3002')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="border border-ink bg-paper p-5 md:p-6">
      <h2 className="text-lg font-semibold mb-1">AI 问答</h2>
      <p className="text-sm text-ash mb-4">{'\u57fa\u4e8e\u5411\u91cf RAG \u68c0\u7d22\uff0c\u9488\u5bf9\u300c'}{entryName}{'\u300d\u7684\u77e5\u8bc6\u7247\u6bb5\u56de\u7b54\u3002'}</p>
      <form onSubmit={submit} className="space-y-3">
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          rows={3}
          placeholder={'\u4f8b\uff1a\u5982\u4f55\u8c03\u7528 API\uff1f\u9002\u5408\u54ea\u4e9b\u573a\u666f\uff1f'}
          className="w-full border border-smoke px-3 py-2 text-sm leading-relaxed"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="line-border px-4 py-2 text-sm font-medium hover:bg-ink hover:text-paper disabled:opacity-40"
        >
          {loading ? '\u601d\u8003\u4e2d\u2026' : '\u63d0\u95ee'}
        </button>
      </form>
      {answer && (
        <div className="mt-4 pt-4 border-t border-smoke text-sm text-ash leading-relaxed whitespace-pre-wrap">
          {answer}
        </div>
      )}
    </section>
  )
}
