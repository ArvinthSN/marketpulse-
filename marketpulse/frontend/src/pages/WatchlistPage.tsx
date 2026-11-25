import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { StarOff } from 'lucide-react';
import { api } from '../lib/api';
import type { Company } from '../types/market';
import { useWatchlist } from '../stores/watchlist';

export function WatchlistPage() {
  const ids = useWatchlist(s => s.companyIds);
  const remove = useWatchlist(s => s.remove);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(false);
  const [failed, setFailed] = useState<number[]>([]);
  useEffect(() => {
    let active = true;
    setLoading(true); setFailed([]);
    Promise.all(ids.map(id => api.company(id).then(value => ({ value })).catch(() => ({ error: id }))))
      .then(results => { if (!active) return; setCompanies(results.flatMap(r => 'value' in r ? [r.value] : [])); setFailed(results.flatMap(r => 'error' in r ? [r.error] : [])); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [ids]);
  return <main className="page-stack">
    <header className="page-heading"><div><p className="eyebrow">PERSONAL WORKSPACE</p><h1>Your watchlist</h1><p>Companies saved in this browser. Data is retrieved from the MARKETPULSE company registry.</p></div><span className="status-pill">{ids.length} saved</span></header>
    <section className="panel">
      {loading ? <p>Loading watchlist…</p> : ids.length === 0 ? <div className="empty-state"><h2>Your watchlist is empty</h2><p>Search the company directory and add companies to follow.</p><Link to="/companies">Explore companies</Link></div> :
      <div className="table-scroll"><table className="data-table"><thead><tr><th>Company</th><th>Country</th><th>Market cap</th><th>Action</th></tr></thead><tbody>{companies.map(c => <tr key={c.id}><td><Link to={`/companies/${c.id}`} className="company-link">{c.name}</Link></td><td>{c.country_code || '—'}</td><td>{c.market_cap == null ? '—' : c.market_cap.toLocaleString()}</td><td><button className="icon-button" onClick={() => remove(c.id)} aria-label={`Remove ${c.name}`}><StarOff size={16}/></button></td></tr>)}</tbody></table></div>}
      {failed.length > 0 && <p className="muted-text">{failed.length} saved item(s) are no longer available in the registry. Remove them from the list to clear.</p>}
    </section>
  </main>;
}
