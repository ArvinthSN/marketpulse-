import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Search, Star, ChevronLeft, ChevronRight } from 'lucide-react';
import { api } from '../lib/api';
import type { Company, Country, Exchange, SectorOverview } from '../types/market';
import { useWatchlist } from '../stores/watchlist';

const PAGE_SIZE = 50;
export function CompaniesPage() {
  const [params, setParams] = useSearchParams();
  const [query, setQuery] = useState(params.get('q') ?? '');
  const [country, setCountry] = useState(params.get('country') ?? '');
  const [sector, setSector] = useState(params.get('sector') ?? '');
  const [exchange, setExchange] = useState(params.get('exchange') ?? '');
  const [page, setPage] = useState(Number(params.get('page') ?? 0));
  const [companies, setCompanies] = useState<Company[]>([]);
  const [countries, setCountries] = useState<Country[]>([]);
  const [sectors, setSectors] = useState<SectorOverview[]>([]);
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const add = useWatchlist((s) => s.add);
  const has = useWatchlist((s) => s.has);

  useEffect(() => { api.countries().then(setCountries).catch(() => setCountries([])); api.sectors().then(setSectors).catch(() => setSectors([])); api.exchanges().then(setExchanges).catch(() => setExchanges([])); }, []);
  useEffect(() => {
    const timer = window.setTimeout(() => {
      const next = new URLSearchParams();
      if (query.trim()) next.set('q', query.trim());
      if (country) next.set('country', country);
      if (sector) next.set('sector', sector);
      if (exchange) next.set('exchange', exchange);
      if (page) next.set('page', String(page));
      setParams(next, { replace: true });
      setLoading(true); setError('');
      api.companies({ q: query.trim(), country: country || undefined, sector_id: sector ? Number(sector) : undefined, exchange: exchange || undefined, limit: PAGE_SIZE, offset: page * PAGE_SIZE })
        .then(setCompanies).catch((e: Error) => setError(e.message)).finally(() => setLoading(false));
    }, 250);
    return () => window.clearTimeout(timer);
  }, [query, country, sector, exchange, page, setParams]);
  const resetPage = (setter: (value: string) => void) => (value: string) => { setter(value); setPage(0); };
  return <main className="page-stack">
    <header className="page-heading"><div><p className="eyebrow">UNIVERSE</p><h1>Company intelligence</h1><p>Search the registered company universe and open detailed market analytics.</p></div><span className="status-pill">Registry data</span></header>
    <section className="panel">
      <div className="search-field"><Search size={18}/><input value={query} onChange={(e) => { setQuery(e.target.value); setPage(0); }} placeholder="Search company, short name, ISIN or symbol..." /></div>
      <div className="filter-row">
        <select value={country} onChange={(e) => resetPage(setCountry)(e.target.value)}><option value="">All countries</option>{countries.map(c => <option key={c.code} value={c.code}>{c.name}</option>)}</select>
        <select value={sector} onChange={(e) => resetPage(setSector)(e.target.value)}><option value="">All sectors</option>{sectors.map(s => <option key={s.sector_id} value={s.sector_id}>{s.sector_name}</option>)}</select>
        <select value={exchange} onChange={(e) => resetPage(setExchange)(e.target.value)}><option value="">All exchanges</option>{exchanges.map(x => <option key={x.code} value={x.code}>{x.name} ({x.code})</option>)}</select>
      </div>
    </section>
    <section className="panel">
      {loading ? <p>Loading registered companies…</p> : error ? <p className="error-text">{error}</p> : companies.length === 0 ? <p>No matching companies found. Try changing your search or filters.</p> :
      <div className="table-scroll"><table className="data-table"><thead><tr><th>Company</th><th>Country</th><th>Sector ID</th><th>Market cap</th><th>Watchlist</th></tr></thead><tbody>{companies.map(c => <tr key={c.id}><td><Link to={`/companies/${c.id}`} className="company-link">{c.name}</Link><small>{c.short_name || `Company #${c.id}`}</small></td><td>{c.country_code || '—'}</td><td>{c.sector_id ?? '—'}</td><td>{c.market_cap == null ? '—' : c.market_cap.toLocaleString()}</td><td><button className="icon-button" aria-label={has(c.id) ? 'Already in watchlist' : 'Add to watchlist'} disabled={has(c.id)} onClick={() => add(c.id)}><Star size={16}/></button></td></tr>)}</tbody></table></div>}
      <div className="pagination"><button disabled={page === 0 || loading} onClick={() => setPage(p => Math.max(0, p - 1))}><ChevronLeft size={16}/> Previous</button><span>Page {page + 1}</span><button disabled={loading || companies.length < PAGE_SIZE} onClick={() => setPage(p => p + 1)}>Next <ChevronRight size={16}/></button></div>
    </section>
  </main>;
}
