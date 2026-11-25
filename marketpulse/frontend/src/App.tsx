import { Navigate, Route, Routes } from 'react-router-dom';
import { AppShell } from './components/AppShell';
import { OverviewPage } from './pages/OverviewPage';
import { WorldMapPage } from './pages/WorldMapPage';
import { PlaceholderPage } from './pages/PlaceholderPage';

export default function App() {
  return <Routes>
    <Route element={<AppShell />}>
      <Route index element={<OverviewPage />} />
      <Route path="world" element={<WorldMapPage />} />
      <Route path="markets" element={<PlaceholderPage title="Global markets" description="Country and exchange dashboards with market coverage, indices and company rankings." />} />
      <Route path="sectors" element={<PlaceholderPage title="Sector heatmap" description="A market-cap-sized treemap with performance periods and sector-to-company drill-down." />} />
      <Route path="companies" element={<PlaceholderPage title="Company intelligence" description="Company search, financial performance, historical charts and data-quality context." />} />
      <Route path="watchlist" element={<PlaceholderPage title="Your watchlist" description="A personal workspace for tracking selected instruments and their latest available quotes." />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Route>
  </Routes>;
}
