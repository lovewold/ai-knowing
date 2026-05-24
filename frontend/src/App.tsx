import { Navigate, Route, Routes } from 'react-router-dom'
import AppShell from './components/AppShell'
import HomePage from './pages/HomePage'
import NewsPage from './pages/NewsPage'
import ReportsPage from './pages/ReportsPage'
import ReportDetailPage from './pages/ReportDetailPage'
import AgentToolsPage from './pages/AgentToolsPage'
import AgentToolDetailPage from './pages/AgentToolDetailPage'
import KnowledgePage from './pages/KnowledgePage'
import KnowledgeDetailPage from './pages/KnowledgeDetailPage'
import ModelMarketPage from './pages/ModelMarketPage'
import ModelMarketDetailPage from './pages/ModelMarketDetailPage'
import AdminLayout from './pages/admin/AdminLayout'
import AdminDashboard from './pages/admin/AdminDashboard'
import AdminModelsPage from './pages/admin/AdminModelsPage'
import AdminCombosPage from './pages/admin/AdminCombosPage'
import AdminConfigPage from './pages/admin/AdminConfigPage'
import AdminKnowledgePage from './pages/admin/AdminKnowledgePage'
import AdminKnowledgeEditPage from './pages/admin/AdminKnowledgeEditPage'

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<HomePage />} />
        <Route path="news" element={<NewsPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="reports/:id" element={<ReportDetailPage />} />
        <Route path="agents" element={<AgentToolsPage />} />
        <Route path="agents/:id" element={<AgentToolDetailPage />} />
        <Route path="knowledge" element={<KnowledgePage />} />
        <Route path="knowledge/:id" element={<KnowledgeDetailPage />} />
        <Route path="models" element={<ModelMarketPage />} />
        <Route path="models/:slug" element={<ModelMarketDetailPage />} />
        <Route path="hotspot" element={<Navigate to="/news" replace />} />
        <Route path="articles" element={<Navigate to="/news?view=list" replace />} />
        <Route path="briefing" element={<Navigate to="/" replace />} />
        <Route path="briefing/:id" element={<Navigate to="/" replace />} />
        <Route path="sources" element={<Navigate to="/admin/config?tab=sources" replace />} />
      </Route>
      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<AdminDashboard />} />
        <Route path="models" element={<AdminModelsPage />} />
        <Route path="combos" element={<AdminCombosPage />} />
        <Route path="config" element={<AdminConfigPage />} />
        <Route path="knowledge" element={<AdminKnowledgePage />} />
        <Route path="knowledge/:id/edit" element={<AdminKnowledgeEditPage />} />
      </Route>
    </Routes>
  )
}
