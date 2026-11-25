import { useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import Plot from 'react-plotly.js';
import { ArrowRight, Globe2, RefreshCw } from 'lucide-react';
import { api } from '../lib/api';
import { ErrorState, LoadingState } from '../components/StateView';
import { formatCompact, formatPercent } from '../lib/format';

export function SectorHeatmapPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [period] = useState('1D');
  const countryCode = searchParams.get('country') ?? '';
  const countriesQuery = useQuery({ queryKey: ['countries'], queryFn: ({ signal }) => api.countries(signal) });
  const sectorsQuery = useQuery({
    queryKey: ['sector-heatmap', countryCode, period],
    queryFn: ({ signal }) => countryCode ? api.countrySectors(countryCode, signal) : api.sectors(signal),
    refetchInterval: 60_000
  });
  const sectors = sectorsQuery.data ?? [];
  const chartSectors = useMemo(() => sectors.filter(item => item.total_market_cap != null && item.total_market_cap > 0), [sectors]);
  const unavailable = sectors.length - chartSectors.length;
  const totalCap = chartSectors.reduce((sum, item) => sum + (item.total_market_cap ?? 0), 0);
  const sourceStatus = sectors.length ? 'Persisted daily observations' : 'Waiting for analytics data';

  return <div className="drill-page">
    <div className="page-heading drill-heading">
      <div><div className="eyebrow">MARKET STRUCTURE <span className="eyebrow-line"/></div><h1>Sector <em>heatmap.</em></h1><p>Explore market-cap distribution and daily sector performance across the global market or a selected country.</p></div>
      <div className="drill-actions">
        <label className="filter-select"><Globe2 size={14}/><select value={countryCode} onChange={event => setSearchParams(event.target.value ? { country: event.target.value } : {})}><option value="">Global market</option>{(countriesQuery.data ?? []).map(country => <option key={country.code} value={country.code}>{country.name}</option>)}</select></label>
        <button className="refresh-button" onClick={() => void sectorsQuery.refetch()}><RefreshCw size={13}/> Refresh</button>
      </div>
    </div>
    <div className="drill-context"><span><b>SIZE</b> Total company market cap</span><span><b>COLOR</b> Market-cap weighted 1D return</span><span><b>DATA</b> {sourceStatus}</span><span><b>SECTORS</b> {sectors.length}</span></div>
    {sectorsQuery.isLoading ? <LoadingState label="Loading sector analytics"/> : sectorsQuery.isError ? <ErrorState message={sectorsQuery.error.message} onRetry={() => void sectorsQuery.refetch()}/> : chartSectors.length ? <>
      <section className="panel heatmap-panel">
        <div className="section-header"><div><h2>{countryCode ? countriesQuery.data?.find(c => c.code === countryCode)?.name ?? countryCode : 'Global'} sector map</h2><p>Each tile represents a sector. Select a tile to inspect its constituents.</p></div><span className="panel-count">{formatCompact(totalCap)} AGGREGATE CAP</span></div>
        <Plot data={[{ type: 'treemap', labels: chartSectors.map(s => s.sector_name), parents: chartSectors.map(() => ''), values: chartSectors.map(s => s.total_market_cap ?? 0), customdata: chartSectors.map(s => s.sector_id), text: chartSectors.map(s => s.market_cap_weighted_return == null ? 'Return unavailable' : formatPercent(s.market_cap_weighted_return)), texttemplate: '<b>%{label}</b><br>%{text}', hovertemplate: '<b>%{label}</b><br>Market cap: %{value:,.0f}<br>1D return: %{text}<extra></extra>', marker: { colors: chartSectors.map(s => s.market_cap_weighted_return ?? 0), colorscale: [[0, '#a7444b'], [0.5, '#253449'], [1, '#238b72']], cmid: 0, showscale: true, colorbar: { title: '1D %', ticksuffix: '%' }, line: { color: '#0c1420', width: 3 } }, tiling: { pad: 4 }, pathbar: { visible: false } } as any]} layout={{ autosize: true, height: 490, margin: { l: 4, r: 8, t: 8, b: 8 }, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: { color: '#dce6f4', family: 'DM Sans, sans-serif' } }} config={{ responsive: true, displayModeBar: false }} style={{ width: '100%' }} onClick={event => { const id = event.points?.[0]?.customdata; if (typeof id === 'number') window.location.assign(`/sectors/${id}${countryCode ? `?country=${countryCode}` : ''}`); }}/>
      </section>
      {unavailable > 0 && <p className="drill-note">{unavailable} sector(s) are not plotted because a positive market-cap value is unavailable. They are not assigned artificial tile sizes.</p>}
      <section className="panel drill-table-panel"><div className="section-header"><div><h2>Sector breakdown</h2><p>Exact values behind the heatmap</p></div></div><div className="drill-table-wrap"><table className="drill-table"><thead><tr><th>SECTOR</th><th>MARKET CAP</th><th>WEIGHTED 1D</th><th>EQUAL 1D</th><th>COMPANIES</th><th></th></tr></thead><tbody>{sectors.map(sector => <tr key={sector.sector_id}><td><strong>{sector.sector_name}</strong></td><td>{formatCompact(sector.total_market_cap)}</td><td className={sector.market_cap_weighted_return == null ? '' : sector.market_cap_weighted_return >= 0 ? 'positive-number' : 'negative-number'}>{formatPercent(sector.market_cap_weighted_return)}</td><td>{formatPercent(sector.equal_weighted_return)}</td><td>{sector.valid_companies}/{sector.listed_companies}</td><td><Link to={`/sectors/${sector.sector_id}${countryCode ? `?country=${countryCode}` : ''}`}>Explore <ArrowRight size={12}/></Link></td></tr>)}</tbody></table></div></section>
    </> : <div className="panel drill-empty"><h2>No sector heatmap data</h2><p>Sector tiles require persisted company market-cap values and historical observations. Missing values are intentionally not represented as zero.</p></div>}
    <div className="dashboard-footer"><span>MARKETPULSE · SECTOR INTELLIGENCE</span><span>Daily snapshot · Not live streaming</span></div>
  </div>;
}
