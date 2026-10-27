import { Routes, Route, Navigate } from 'react-router-dom'
import { GraphExplorerPage } from '@/pages/GraphExplorerPage'
import { OverviewPage } from '@/pages/OverviewPage'
import { ValidationPage } from '@/pages/ValidationPage'
import { PerformancePage } from '@/pages/PerformancePage'

export function App() {
  return (
    <Routes>
      <Route path="/" element={<GraphExplorerPage />} />
      <Route path="/graph-explorer" element={<GraphExplorerPage />} />
      <Route path="/overview" element={<OverviewPage />} />
      <Route path="/validation" element={<ValidationPage />} />
      <Route path="/performance" element={<PerformancePage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
