import { Link, useParams, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, ArrowUpRight, ArrowDownRight, Building2 } from 'lucide-react';
import { api } from '../lib/api';
import { MetricCard } from '../components/MetricCard';
import { ErrorState, LoadingState } from '../components/StateView';
import { formatCompact, formatPercent } from '../lib/format';

export function SectorDetailPage() {
  const { sectorId = '' } = useParams();
  const id = Number(sectorId);
  const [params] = useSearchParams();
  const country = params.get('country') ?? '';
  const overview = useQuery({ queryKey: ['sector-overview', id, country], queryFn: ({ signal }) => api.sectorOverview(id, country || undefined, signal), enabled: Number.isInteger(id) && id > 0 });
  const companies = useQuery({ queryKey: ['sector-companies', id, country], queryFn: ({ signal }) => api.sectorCompanies(id, country || undefined, signal), enabled: Number.isInteger(id) && id > 0 });
  if (!Number.isInteger(id) || id <= 0) return <div className="drill-page"><h1>Invalid sector</h1><Link to="/sectors">Back to heatmap</Link></div>;
  if (overview.isLoading) return <div className="drill-page"><LoadingState label="Loading sector detail"/></div>;
  if (overview.isError) return <div className="drill-page"><ErrorState message={overview.error.message} onRetry={() => void overview.refetch()}/></div>;
  const item = overview.data;
  if (!item) return <div className="drill-page"><h1>Sector not found</h1><Link to="/sectors">Back to heatmap</Link></div>;
  const ret = item.market_cap_weighted_return;
  return <div className="drill-page">
    <div className="eyebrow">SECTOR INTELLIGENCE <span className="eyebrow-line"/></div>
    <div className="drill-detail-heading"><div><h1>{item.sector_name} <em>sector.</em></h1><p>{country ? `Country-filtered view · ${country}` : 'Global sector constituents'} · persisted daily observations</p></div><Link className="country-back-link" to={country ? `/sectors?country=${country}` : '/sectors'}><ArrowLeft size={14}/> Back to heatmap</Link></div>
    <div className="metrics-grid">
      <MetricCard label="MARKET-CAP WEIGHTED 1D" value={formatPercent(ret)} detail="Weighted by available company market cap" icon={<Building2 size={17}/>} accent={ret == null ? 'blue' : ret >= 0 ? 'green' : 'amber'}/>
      <MetricCard label="EQUAL-WEIGHTED 1D" value={formatPercent(item.equal_weighted_return)} detail="Each valid company weighted equally" icon={<Building2 size={17}/>} accent="blue"/>
      <MetricCard label="TOTAL MARKET CAP" value={formatCompact(item.total_market_cap)} detail="Registry market cap · FX normalization not applied" icon={<Building2 size={17}/>} accent="purple"/>
      <MetricCard label="VALID COMPANIES" value={`${item.valid_companies} / ${item.listed_companies}`} detail="Companies with calculated daily returns" icon={<Building2 size={17}/>} accent="amber"/>
    </div>
    <section className="panel drill-table-panel"><div className="section-header"><div><h2>Sector constituents</h2><p>Company registry records with market-cap values where available</p></div><span className="panel-count">{companies.data?.length ?? 0} COMPANIES</span></div>
      {companies.isLoading ? <LoadingState label="Loading constituents"/> : companies.isError ? <ErrorState message={companies.error.message} onRetry={() => void companies.refetch()}/> : companies.data?.length ? <div className="drill-table-wrap"><table className="drill-table"><thead><tr><th>COMPANY</th><th>RAW MARKET CAP</th><th>COUNTRY</th><th></th></tr></thead><tbody>{companies.data.map(company => <tr key={company.company_id}><td><strong>{company.name}</strong></td><td>{formatCompact(company.market_cap)}</td><td>{company.country_code ?? '—'}</td><td><Link to={`/companies/${company.company_id}`}>Company profile <ArrowUpRight size={12}/></Link></td></tr>)}</tbody></table></div> : <div className="drill-empty">No companies are currently classified in this sector.</div>}
    </section>
    <p className="drill-note"><ArrowDownRight size={13}/> Volume is not displayed because the sector aggregation endpoint does not currently provide a verified total-volume metric.</p>
  </div>;
}
