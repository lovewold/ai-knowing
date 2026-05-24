import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { getAdminToken, setAdminToken } from '../../api/admin'

const links = [
  { to: '/admin', label: '概览', end: true },
  { to: '/admin/models', label: '多模型', end: false },
  { to: '/admin/combos', label: 'Agent组合', end: false },
  { to: '/admin/config', label: '配置', end: false },
]

export default function AdminLayout() {
  const navigate = useNavigate()
  const [token, setToken] = useState(getAdminToken())
  const [input, setInput] = useState(token)

  function saveToken() {
    setAdminToken(input.trim())
    setToken(input.trim())
  }

  return (
    <div className="min-h-screen bg-paper flex">
      <aside className="w-52 border-r border-ink shrink-0 flex flex-col">
        <div className="p-4 border-b border-ink">
          <p className="font-serif font-semibold">管理后台</p>
          <p className="text-[10px] font-mono text-silver mt-1">AI全知 Admin</p>
        </div>
        <nav className="flex-1 p-2">
          {links.map(({ to, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `block px-3 py-2 text-sm mb-1 ${isActive ? 'bg-ink text-paper' : 'text-ash hover:bg-mist'}`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="p-3 border-t border-ink space-y-2">
          <input
            type="password"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Admin Token"
            className="w-full text-xs border border-smoke px-2 py-1.5 font-mono"
          />
          <button type="button" onClick={saveToken} className="w-full text-xs border border-ink py-1 hover:bg-mist">
            保存 Token
          </button>
          <button type="button" onClick={() => navigate('/')} className="w-full text-xs text-silver underline">
            返回前台
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
