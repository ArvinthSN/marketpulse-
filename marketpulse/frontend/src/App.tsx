import { Navigate, Route, Routes } from 'react-router-dom';
import { AppShell } from './components/AppShell';
import { OverviewPage } from './pages/OverviewPage';
import { WorldMapPage } from './pages/WorldMapPage';
import { PlaceholderPage } from './pages/PlaceholderPage';
import { MarketsPage } from './pages/MarketsPage';
import { CountryDashboardPage } from './pages/CountryDashboardPage';
import { SectorHeatmapPage } from './pages/SectorHeatmapPage';
import { SectorDetailPage } from './pages/SectorDetailPage';
import { CompanyDetailPage } from './pages/CompanyDetailPage';

export default function App() {
  return <Routes>
    <Route element={<AppShell />}>
      <Route index element={<OverviewPage />} />
      <Route path="world" element={<WorldMapPage />} />
      <Route path="markets" element={<MarketsPage />} />
      <Route path="markets/:countryCode" element={<CountryDashboardPage />} />
      <Route path="sectors" element={<SectorHeatmapPage />} />
      <Route path="sectors/:sectorId" element={<SectorDetailPage />} />
      <Route path="companies" element={<PlaceholderPage title="Company intelligence" description="Open a company from the sector drill-down to view its profile, performance and historical price observations." />} />
      <Route path="companies/:companyId" element={<CompanyDetailPage />} />
      <Route path="watchlist" element={<PlaceholderPage title="Your watchlist" description="A personal workspace for tracking selected instruments and their latest available quotes." />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Route>
  </Routes>;
}
