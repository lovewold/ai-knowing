import { useEffect, useState } from 'react'
import { adminApi, type AdminStats } from '../../api/admin'

export default function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    adminApi.getStats().then(setStats).catch((e) => {
      setError(e.message === 'UNAUTHORIZED' ? '请在左侧设置 Admin Token（后端 .env 中 ADMIN_TOKEN）' : '加载失败')
    })
  }, [])

  const cards = stats
    ? [
        ['资讯', stats.articles],
        ['报告', stats.reports],
        ['高信号', stats.high_signal],
        ['Agent工具', stats.agent_tools],
        ['晨报', stats.briefings],
        ['LLM模型', stats.llm_models],
        ['Agent组合', stats.agent_combos],
        ['数据源', stats.sources],
      ]
    : []

  return (
    <div className="p-8 max-w-4xl">
      <h1 className="font-serif text-2xl font-semibold mb-2">系统概览</h1>
      <p className="text-sm text-ash mb-8">管理多模型配置、Agent 组合与系统参数</p>
      {error && <p className="text-sm text-red-700 font-mono mb-4">{error}</p>}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {cards.map(([label, value]) => (
            <div key={String(label)} className="border border-ink p-4">
              <p className="text-[10px] font-mono text-silver uppercase">{label}</p>
              <p className="font-serif text-2xl font-semibold mt-1">{value}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
