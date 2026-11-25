import { NavLink, Outlet } from 'react-router-dom';
import { Activity, BarChart3, Building2, Globe2, LayoutDashboard, Map, Search, Settings, Star } from 'lucide-react';

const navigation = [
  { to: '/', label: 'Overview', icon: LayoutDashboard, end: true },
  { to: '/world', label: 'World map', icon: Globe2 },
  { to: '/markets', label: 'Markets', icon: Map },
  { to: '/sectors', label: 'Sector heatmap', icon: BarChart3 },
  { to: '/companies', label: 'Companies', icon: Building2 },
  { to: '/watchlist', label: 'Watchlist', icon: Star }
];

export function AppShell() {
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><Activity size={19} /></div><div><strong>MARKETPULSE</strong><span>GLOBAL INTELLIGENCE</span></div></div>
      <div className="workspace-label">WORKSPACE</div>
      <nav className="side-nav">
        {navigation.map(({ to, label, icon: Icon, end }) => <NavLink key={to} to={to} end={end} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}><Icon size={17} /><span>{label}</span></NavLink>)}
      </nav>
      <div className="sidebar-bottom">
        <div className="sidebar-note"><span className="pulse-dot" /><div><strong>Data services</strong><small>Connected to API</small></div></div>
        <button className="nav-link nav-button" type="button"><Settings size={17} /><span>Settings</span></button>
        <div className="profile"><div className="avatar">MP</div><div><strong>MarketPulse</strong><small>Research workspace</small></div></div>
      </div>
    </aside>
    <main className="main-area">
      <header className="topbar">
        <div className="breadcrumb"><span>Workspace</span><span className="crumb-separator">/</span><strong>Market intelligence</strong></div>
        <div className="topbar-actions"><span className="environment-tag">GLOBAL MARKETS</span><button className="icon-button" aria-label="Search"><Search size={17} /></button></div>
      </header>
      <div className="page-content"><Outlet /></div>
    </main>
  </div>;
}
