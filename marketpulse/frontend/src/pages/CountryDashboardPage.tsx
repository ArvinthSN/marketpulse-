import { useMemo } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowDownRight, ArrowLeft, ArrowUpRight, Building2, Globe2, Landmark, RefreshCw, TrendingUp } from 'lucide-react';
import { MetricCard } from '../components/MetricCard';
import { ErrorState, LoadingState } from '../components/StateView';
import { api } from '../lib/api';
import { formatCompact, formatPercent } from '../lib/format';

const percent = (value: number | null | undefined) => value == null ? '—' : formatPercent(value);

export function CountryDashboardPage() {
  const { countryCode = '' } = useParams();
  const code = countryCode.toUpperCase();
  const registryQuery = useQuery({ queryKey: ['country-registry', code], queryFn: ({ signal }) => api.countries(signal) });
  const overviewQuery = useQuery({ queryKey: ['country-overview', code], queryFn: ({ signal }) => api.countryOverview(code, signal), enabled: !!code, refetchInterval: 60_000 });
  const exchangesQuery = useQuery({ queryKey: ['country-exchanges', code], queryFn: ({ signal }) => api.exchanges(code, signal), enabled: !!code });
  const companiesQuery = useQuery({ queryKey: ['country-company-registry', code], queryFn: ({ signal }) => api.companies({ country: code, limit: 100 }, signal), enabled: !!code });
  const performanceQuery = useQuery({ queryKey: ['country-company-performance', code], queryFn: ({ signal }) => api.countryCompanies(code, 100, signal), enabled: !!code, refetchInterval: 60_000 });
  const gainersQuery = useQuery({ queryKey: ['country-gainers', code], queryFn: ({ signal }) => api.countryGainers(code, 10, signal), enabled: !!code, refetchInterval: 60_000 });
  const losersQuery = useQuery({ queryKey: ['country-losers', code], queryFn: ({ signal }) => api.countryLosers(code, 10, signal), enabled: !!code, refetchInterval: 60_000 });

  const country = registryQuery.data?.find(item => item.code.toUpperCase() === code);
  const performanceMap = useMemo(() => new Map((performanceQuery.data ?? []).map(item => [item.company_id, item])), [performanceQuery.data]);
  const companies = (companiesQuery.data ?? []).map(company => ({ ...company, performance: performanceMap.get(company.id) }));
  const validCompanies = performanceQuery.data?.filter(item => item.performance['1D'] != null).length ?? 0;
  const loading = registryQuery.isLoading || overviewQuery.isLoading;
  const error = registryQuery.error ?? overviewQuery.error;

  if (loading) return <div className="country-dashboard"><LoadingState label={`Loading ${code} market dashboard…`} /></div>;
  if (error) return <div className="country-dashboard"><ErrorState message={error.message} onRetry={() => { void registryQuery.refetch(); void overviewQuery.refetch(); }} /><Link className="country-back-link" to="/world"><ArrowLeft size={14}/> Back to world map</Link></div>;
  if (!country) return <div className="country-dashboard"><div className="eyebrow">COUNTRY MARKET INTELLIGENCE</div><h1>Country not found</h1><p className="country-subtitle">The country code {code} is not present in the configured country registry.</p><Link className="country-back-link" to="/world"><ArrowLeft size={14}/> Back to world map</Link></div>;

  const overview = overviewQuery.data;
  const status = overview?.data_status ?? 'UNKNOWN';
  const coverage = overview?.coverage;
  const refresh = () => { void overviewQuery.refetch(); void exchangesQuery.refetch(); void companiesQuery.refetch(); void performanceQuery.refetch(); void gainersQuery.refetch(); void losersQuery.refetch(); };
  const renderMovers = (items: { company_id: number; name: string; return_percentage: number }[] | undefined, positive: boolean) => items?.length ? items.map((item, index) => <div className="country-mover-row" key={item.company_id}><span className="mover-rank">{String(index + 1).padStart(2, '0')}</span><span className="mover-name">{item.name}</span><strong className={positive ? 'positive-number' : 'negative-number'}>{positive ? <ArrowUpRight size={13}/> : <ArrowDownRight size={13}/>} {percent(item.return_percentage)}</strong></div>) : <div className="country-inline-empty">No qualifying daily observations are available.</div>;

  return <div className="country-dashboard">
    <div className="country-dashboard-heading">
      <div><div className="eyebrow"><Globe2 size={12}/> COUNTRY MARKET INTELLIGENCE <span className="eyebrow-line"/></div><h1>{country.name} <em>markets.</em></h1><p className="country-subtitle">{country.code} · {country.currency} · {country.timezone}</p></div>
      <div className="country-heading-actions"><span className={`status-pill ${status === 'PARTIAL' ? 'status-partial' : status === 'UNAVAILABLE' ? 'status-unavailable' : ''}`}><i className="status-dot"/>{status}</span><button className="refresh-button" onClick={refresh}><RefreshCw size={13}/> Refresh data</button></div>
    </div>
    <div className="country-breadcrumb"><Link to="/world">World map</Link><span>/</span><strong>{country.name}</strong></div>
    <div className="metrics-grid country-metrics-grid">
      <MetricCard label="MARKET-CAP WEIGHTED RETURN" value={percent(overview?.market_cap_weighted_return)} detail="Based on available daily observations" icon={<TrendingUp size={16}/>} accent="green"/>
      <MetricCard label="EQUAL-WEIGHTED RETURN" value={percent(overview?.equal_weighted_return)} detail="Company returns weighted equally" icon={<TrendingUp size={16}/>} accent="blue"/>
      <MetricCard label="TRACKED COMPANIES" value={(overview?.tracked_companies ?? 0).toLocaleString()} detail={`${validCompanies.toLocaleString()} with a calculated 1D return`} icon={<Building2 size={16}/>} accent="purple"/>
      <MetricCard label="REGISTERED EXCHANGES" value={exchangesQuery.data?.length == null ? '—' : String(exchangesQuery.data.length)} detail="Configured exchange registry" icon={<Landmark size={16}/>} accent="amber"/>
    </div>
    <div className="country-data-context">
      <span><b>DATA COVERAGE</b> {coverage ? `${coverage.available} / ${coverage.expected} companies` : 'Not reported'}</span>
      <span><b>LAST SOURCE OBSERVATION</b> {overview?.source_observation_at ? new Date(overview.source_observation_at).toLocaleString() : 'Unavailable'}</span>
      <span><b>REPORTING CURRENCY</b> {overview?.reporting_currency ?? country.currency}</span>
      <span><b>DATA MODE</b> Persisted daily snapshot</span>
    </div>
    <div className="country-dashboard-grid">
      <section className="panel">
        <div className="section-header"><div><h2>Exchange coverage</h2><p>Exchanges configured for this country</p></div><span className="panel-count">{exchangesQuery.data?.length ?? 0} REGISTERED</span></div>
        {exchangesQuery.isLoading ? <LoadingState label="Loading exchanges"/> : exchangesQuery.isError ? <ErrorState message={exchangesQuery.error.message} onRetry={() => void exchangesQuery.refetch()}/> : exchangesQuery.data?.length ? <div className="country-exchange-grid">{exchangesQuery.data.map(exchange => <article className="country-exchange-card" key={exchange.id}><div><strong>{exchange.code}</strong><span className={exchange.enabled ? 'exchange-enabled' : 'exchange-disabled'}>{exchange.enabled ? 'ENABLED' : 'DISABLED'}</span></div><p>{exchange.name}</p><small>{exchange.currency} · {exchange.timezone}</small></article>)}</div> : <div className="country-inline-empty">No exchanges are registered for this country yet.</div>}
      </section>
      <section className="panel">
        <div className="section-header"><div><h2>Market breadth</h2><p>Companies with valid daily return observations</p></div></div>
        {overview?.breadth ? <div className="country-breadth"><div><span>Advancing</span><strong className="positive-number">{overview.breadth.advancing}</strong></div><div><span>Declining</span><strong className="negative-number">{overview.breadth.declining}</strong></div><div><span>Unchanged</span><strong>{overview.breadth.unchanged}</strong></div><div><span>Advance / decline</span><strong>{overview.breadth.advance_decline_ratio == null ? '—' : overview.breadth.advance_decline_ratio.toFixed(2)}</strong></div></div> : <div className="country-inline-empty">Breadth data is unavailable.</div>}
      </section>
      <section className="panel">
        <div className="section-header"><div><h2>Top gainers</h2><p>Highest positive 1D returns in the country dataset</p></div><span className="mover-section-tag positive-number">1D</span></div>
        {gainersQuery.isLoading ? <LoadingState label="Loading gainers"/> : gainersQuery.isError ? <ErrorState message={gainersQuery.error.message} onRetry={() => void gainersQuery.refetch()}/> : renderMovers(gainersQuery.data, true)}
      </section>
      <section className="panel">
        <div className="section-header"><div><h2>Top losers</h2><p>Lowest negative 1D returns in the country dataset</p></div><span className="mover-section-tag negative-number">1D</span></div>
        {losersQuery.isLoading ? <LoadingState label="Loading losers"/> : losersQuery.isError ? <ErrorState message={losersQuery.error.message} onRetry={() => void losersQuery.refetch()}/> : renderMovers(losersQuery.data, false)}
      </section>
    </div>
    <section className="panel country-company-panel">
      <div className="section-header"><div><h2>Tracked companies</h2><p>Company registry joined with available 1D performance calculations</p></div><span className="panel-count">{companies.length} LISTED</span></div>
      {companiesQuery.isLoading || performanceQuery.isLoading ? <LoadingState label="Loading country companies"/> : companiesQuery.isError ? <ErrorState message={companiesQuery.error.message} onRetry={() => void companiesQuery.refetch()}/> : companies.length ? <div className="country-company-table-wrap"><table className="country-company-table"><thead><tr><th>COMPANY</th><th>SECTOR ID</th><th>MARKET CAP</th><th>1D RETURN</th><th>OBSERVATION</th></tr></thead><tbody>{companies.map(company => <tr key={company.id}><td><strong>{company.short_name || company.name}</strong><small>{company.name}</small></td><td>{company.sector_id ?? '—'}</td><td>{company.market_cap == null ? '—' : formatCompact(company.market_cap)}</td><td className={(company.performance?.performance['1D'] ?? 0) > 0 ? 'positive-number' : (company.performance?.performance['1D'] ?? 0) < 0 ? 'negative-number' : ''}>{percent(company.performance?.performance['1D'])}</td><td>{company.performance?.data_quality.last_market_observation ? new Date(company.performance.data_quality.last_market_observation).toLocaleDateString() : 'Unavailable'}</td></tr>)}</tbody></table></div> : <div className="country-inline-empty">No companies are currently registered for {country.name}.</div>}
    </section>
    <div className="country-dashboard-footer">MARKETPULSE · {country.code} · Daily analytics snapshot · Values are shown only when source observations support them</div>
  </div>;
}
