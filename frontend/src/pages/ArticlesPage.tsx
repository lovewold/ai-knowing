import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { Article } from '../types'
import ArticleRow from '../components/ArticleRow'
import EmptyState from '../components/EmptyState'

export default function ArticlesPage() {
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getArticles(undefined, 45).then(setArticles).catch(console.error).finally(() => setLoading(false))
  }, [])

  const highCount = articles.filter(a => a.signal_status === 'high').length

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      <header className="mb-10 pb-6 border-b border-ink">
        <h1 className="font-serif text-3xl font-semibold">实时资讯</h1>
        <p className="mt-2 text-sm text-ash">按信噪比分排序 · 高信号 {highCount} 条</p>
      </header>
      {loading ? <p className="text-sm text-silver font-mono">加载中...</p>
        : articles.length ? articles.map((a, i) => <ArticleRow key={a.id} article={a} index={i} />)
        : <EmptyState title="暂无资讯" description="点击抓取更新" />}
    </div>
  )
}
