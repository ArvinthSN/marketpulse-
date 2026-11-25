import { Link, useParams } from 'react-router-dom';
import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import Plot from 'react-plotly.js';
import { ArrowLeft, Building2, ChartLine, Globe2 } from 'lucide-react';
import { api } from '../lib/api';
import { ErrorState, LoadingState } from '../components/StateView';
import { MetricCard } from '../components/MetricCard';
import { formatCompact, formatDate, formatPercent } from '../lib/format';

export function CompanyDetailPage() {
  const { companyId = '' } = useParams();
  const id = Number(companyId);
  const company = useQuery({ queryKey: ['company', id], queryFn: ({ signal }) => api.company(id, signal), enabled: Number.isInteger(id) && id > 0 });
  const performance = useQuery({ queryKey: ['company-performance', id], queryFn: ({ signal }) => api.companyPerformance(id, '1D', signal), enabled: Number.isInteger(id) && id > 0 });
  const metrics = useQuery({ queryKey: ['company-metrics', id], queryFn: ({ signal }) => api.companyMetrics(id, signal), enabled: Number.isInteger(id) && id > 0 });
  const history = useQuery({ queryKey: ['company-history', id], queryFn: ({ signal }) => api.companyHistory(id, 1000, signal), enabled: Number.isInteger(id) && id > 0 });
  const series = useMemo(() => [...(history.data ?? [])].sort((a,b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()), [history.data]);
  if (!Number.isInteger(id) || id <= 0) return <div className="drill-page"><h1>Invalid company</h1><Link to="/companies">Back to companies</Link></div>;
  if (company.isLoading) return <div className="drill-page"><LoadingState label="Loading company profile"/></div>;
  if (company.isError) return <div className="drill-page"><ErrorState message={company.error.message} onRetry={() => void company.refetch()}/></div>;
  if (!company.data) return <div className="drill-page"><h1>Company not found</h1></div>;
  const item = company.data;
  const q = performance.data;
  const last = series[series.length - 1];
  return <div className="drill-page">
    <div className="eyebrow">COMPANY INTELLIGENCE <span className="eyebrow-line"/></div>
    <div className="drill-detail-heading"><div><h1>{item.short_name || item.name} <em>profile.</em></h1><p>{item.name} · {item.country_code ?? 'Country unavailable'} · {q?.symbol ?? 'Symbol unavailable'}</p></div><Link className="country-back-link" to={item.sector_id ? `/sectors/${item.sector_id}` : '/sectors'}><ArrowLeft size={14}/> Back to sector</Link></div>
    <div className="metrics-grid">
      <MetricCard label="MARKET CAP" value={formatCompact(item.market_cap)} detail="Company registry value" icon={<Building2 size={17}/>} accent="blue"/>
      <MetricCard label="1D PERFORMANCE" value={formatPercent(q?.performance['1D'])} detail={q?.price_basis ? `${q.price_basis} price basis` : 'Performance unavailable'} icon={<ChartLine size={17}/>} accent={(q?.performance['1D'] ?? 0) >= 0 ? 'green' : 'amber'}/>
      <MetricCard label="LATEST CLOSE" value={last ? last.close.toLocaleString(undefined,{maximumFractionDigits:2}) : '—'} detail={last ? last.currency : 'No historical price'} icon={<ChartLine size={17}/>} accent="purple"/>
      <MetricCard label="LATEST VOLUME" value={metrics.data?.current_volume == null ? '—' : formatCompact(metrics.data.current_volume)} detail="Latest persisted daily observation" icon={<Globe2 size={17}/>} accent="amber"/>
    </div>
    <div className="drill-context"><span><b>DATA STATUS</b> {q?.data_quality.data_status ?? (performance.isLoading ? 'Loading' : 'Unavailable')}</span><span><b>SOURCE</b> {q?.data_quality.source ?? 'Not reported'}</span><span><b>LAST OBSERVATION</b> {formatDate(q?.data_quality.last_market_observation ?? last?.timestamp)}</span><span><b>PRICE BASIS</b> {q?.price_basis ?? '—'}</span></div>
    <section className="panel company-chart-panel"><div className="section-header"><div><h2>Historical price</h2><p>Daily close observations returned by the historical-price API</p></div><span className="panel-count">{series.length} OBSERVATIONS</span></div>
      {history.isLoading ? <LoadingState label="Loading historical prices"/> : history.isError ? <ErrorState message={history.error.message} onRetry={() => void history.refetch()}/> : series.length ? <Plot data={[{ type:'scatter', mode:'lines', x:series.map(row=>row.timestamp), y:series.map(row=>row.close), line:{ color:'#55b89b', width:2 }, fill:'tozeroy', fillcolor:'rgba(85,184,155,0.08)', hovertemplate:'%{x|%d %b %Y}<br>Close: %{y:,.2f}<extra></extra>' }]} layout={{ autosize:true, height:340, margin:{l:55,r:20,t:10,b:45}, paper_bgcolor:'transparent', plot_bgcolor:'transparent', font:{color:'#9aabc1',family:'DM Sans,sans-serif'}, xaxis:{gridcolor:'#202d3e',linecolor:'#2a394e'}, yaxis:{gridcolor:'#202d3e',linecolor:'#2a394e',title:'Close price'} }} config={{responsive:true,displayModeBar:false}} style={{width:'100%'}}/> : <div className="drill-empty">No historical price observations are available for this company.</div>}
    </section>
    <p className="drill-note">Historical prices are persisted daily observations, not live quotes. The chart uses unadjusted close values and the observation currency shown in the source data.</p>
  </div>;
}
