import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import ReportsPage from './pages/ReportsPage'
import ReportDetailPage from './pages/ReportDetailPage'
import ArticlesPage from './pages/ArticlesPage'
import AgentToolsPage from './pages/AgentToolsPage'
import DailyBriefingPage from './pages/DailyBriefingPage'
import SourcesPage from './pages/SourcesPage'
import HotspotPage from './pages/HotspotPage'
import AdminLayout from './pages/admin/AdminLayout'
import AdminDashboard from './pages/admin/AdminDashboard'
import AdminModelsPage from './pages/admin/AdminModelsPage'
import AdminCombosPage from './pages/admin/AdminCombosPage'
import AdminConfigPage from './pages/admin/AdminConfigPage'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="reports/:id" element={<ReportDetailPage />} />
        <Route path="articles" element={<ArticlesPage />} />
        <Route path="hotspot" element={<HotspotPage />} />
        <Route path="agents" element={<AgentToolsPage />} />
        <Route path="briefing" element={<DailyBriefingPage />} />
        <Route path="briefing/:id" element={<DailyBriefingPage />} />
        <Route path="sources" element={<SourcesPage />} />
      </Route>
      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<AdminDashboard />} />
        <Route path="models" element={<AdminModelsPage />} />
        <Route path="combos" element={<AdminCombosPage />} />
        <Route path="config" element={<AdminConfigPage />} />
      </Route>
    </Routes>
  )
}
