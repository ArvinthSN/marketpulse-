import { useMemo, useState } from 'react';
import { geoNaturalEarth1, geoPath, geoGraticule10 } from 'd3-geo';
import { feature } from 'topojson-client';
import type { Feature, FeatureCollection, Geometry } from 'geojson';
import type { Topology, GeometryCollection } from 'topojson-specification';
import worldTopology from 'world-atlas/countries-110m.json';
import isoCountries from 'i18n-iso-countries';
import { ArrowDownRight, ArrowUpRight, Globe2, Info, MapPinned, RefreshCw } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { formatCompact, formatPercent } from '../lib/format';
import { ErrorState, LoadingState } from '../components/StateView';

type Props = { name?: string };
type Region = 'All regions' | 'Americas' | 'Europe' | 'Asia Pacific' | 'Middle East & Africa';
type WorldFeature = Feature<Geometry, Props> & { id?: string | number };
const regions: { label: Region; codes: string[] }[] = [
 { label:'Americas',codes:['US','CA','MX','BR','AR','CL','CO','PE'] },
 { label:'Europe',codes:['GB','DE','FR','IT','ES','NL','CH','SE','NO','FI','DK','PL','BE','AT','IE','PT','GR'] },
 { label:'Asia Pacific',codes:['IN','JP','CN','HK','KR','TW','SG','AU','NZ','ID','MY','TH','VN','PH'] },
 { label:'Middle East & Africa',codes:['AE','SA','QA','KW','BH','OM','IL','TR','ZA','NG','EG','KE','MA'] }
];
const topology = worldTopology as unknown as Topology<{ countries: GeometryCollection<Props> }>;
const worldFeatures = feature(topology, topology.objects.countries) as FeatureCollection<Geometry, Props>;
const toAlpha2 = (id: string | number | undefined) => {
 if (id == null) return '';
 const alpha3 = isoCountries.numericToAlpha3(String(id).padStart(3,'0'));
 return alpha3 ? isoCountries.alpha3ToAlpha2(alpha3) || '' : '';
};
const pct = (value: number | null | undefined) => value == null ? '—' : formatPercent(value);

export function WorldMapPage() {
 const [region,setRegion] = useState<Region>('All regions');
 const [selectedCode,setSelectedCode] = useState<string|null>(null);
 const [zoom,setZoom] = useState(1);
 const registryQuery = useQuery({queryKey:['world-registry'],queryFn:({signal})=>api.countries(signal)});
 const analyticsQuery = useQuery({queryKey:['world-analytics'],queryFn:({signal})=>api.globalCountries(signal),refetchInterval:60_000});
 const detailQuery = useQuery({queryKey:['world-country',selectedCode],queryFn:({signal})=>api.countryOverview(selectedCode!,signal),enabled:!!selectedCode});
 const exchangesQuery = useQuery({queryKey:['world-country-exchanges',selectedCode],queryFn:({signal})=>api.exchanges(selectedCode!,signal),enabled:!!selectedCode});
 const registry = registryQuery.data ?? [];
 const analytics = analyticsQuery.data ?? [];
 const registryMap = useMemo(()=>new Map(registry.map(x=>[x.code,x])),[registry]);
 const analyticsMap = useMemo(()=>new Map(analytics.map(x=>[x.country_code,x])),[analytics]);
 const regionSpec = regions.find(x=>x.label===region);
 const rows = analytics.filter(x=>!regionSpec || regionSpec.codes.includes(x.country_code));
 const ranked = rows.filter(x=>x.market_cap_weighted_return!=null).sort((a,b)=>(b.market_cap_weighted_return??0)-(a.market_cap_weighted_return??0));
 const gainers = ranked.filter(x=>(x.market_cap_weighted_return??0)>0).slice(0,5);
 const losers = [...ranked].filter(x=>(x.market_cap_weighted_return??0)<0).reverse().slice(0,5);
 const projection = useMemo(()=>geoNaturalEarth1().fitExtent([[12,12],[968,510]],worldFeatures),[]);
 const path = useMemo(()=>geoPath(projection),[projection]);
 const graticule = useMemo(()=>path(geoGraticule10())??'', [path]);
 const selectedRegistry = selectedCode ? registryMap.get(selectedCode) : undefined;
 const loading = registryQuery.isLoading || analyticsQuery.isLoading;
 const error = registryQuery.error ?? analyticsQuery.error;
 const fillFor = (code:string) => {
  const v=analyticsMap.get(code)?.market_cap_weighted_return;
  if(v==null)return '#202a35';
  const n=Math.min(Math.abs(v)/4,1);
  return v>=0 ? `rgba(28,${Math.round(105+n*95)},${Math.round(75+n*55)},${.52+n*.38})` : `rgba(${Math.round(130+n*80)},${Math.round(48+n*25)},${Math.round(57+n*30)},${.52+n*.38})`;
 };
 return <div className="world-page">
  <div className="world-heading"><div><div className="eyebrow">GLOBAL MARKET INTELLIGENCE <span className="eyebrow-line"/></div><h1>World <em>map.</em></h1><p>Explore country-level market performance from persisted observations.</p></div><div className="world-live-state"><span className="snapshot-dot"/> ANALYTICS SNAPSHOT <button onClick={()=>{void registryQuery.refetch();void analyticsQuery.refetch();}} aria-label="Refresh map data"><RefreshCw size={14}/></button></div></div>
  <div className="world-toolbar"><div className="region-tabs"><button className={region==='All regions'?'active':''} onClick={()=>setRegion('All regions')}>World</button>{regions.map(x=><button key={x.label} className={region===x.label?'active':''} onClick={()=>setRegion(x.label)}>{x.label}</button>)}</div><div className="world-view-tabs"><span className="selected">Performance</span><span className="disabled" title="Not supported by the current country analytics API">Market cap</span><span className="disabled" title="Not supported by the current country analytics API">Volume</span><b>1D</b></div></div>
  {error && <ErrorState message={error.message} onRetry={()=>{void registryQuery.refetch();void analyticsQuery.refetch();}}/>}
  {loading ? <div className="world-loading"><LoadingState label="Loading country registry and analytics"/></div> : <>
   <div className="world-layout">
    <section className="world-map-panel"><div className="map-panel-top"><span><Globe2 size={14}/> WORLD PERFORMANCE</span><span>{rows.length} COUNTRIES WITH ANALYTICS</span></div>
     <div className="map-canvas"><svg viewBox="0 0 980 525" role="img" aria-label="World map shaded by country market performance"><defs><radialGradient id="mapGlow"><stop offset="0%" stopColor="#142235"/><stop offset="100%" stopColor="#0b111a"/></radialGradient></defs><rect width="980" height="525" fill="url(#mapGlow)"/><path d={graticule} className="map-graticule"/><g transform={`translate(490 262) scale(${zoom}) translate(-490 -262)`}>{worldFeatures.features.map((f:WorldFeature,i)=>{
      const code=toAlpha2(f.id); const country=registryMap.get(code); const has=analyticsMap.has(code); const muted=!!regionSpec&&!regionSpec.codes.includes(code);
      return <path key={code||String(f.id)||i} d={path(f)??''} fill={fillFor(code)} className={`map-country ${muted?'map-country-muted':''} ${selectedCode===code?'map-country-selected':''}`} onClick={()=>country&&setSelectedCode(code)} tabIndex={country?0:-1} role={country?'button':undefined} aria-label={country?`${country.name}, ${pct(analyticsMap.get(code)?.market_cap_weighted_return)}`:f.properties?.name} onKeyDown={e=>{if(country&&(e.key==='Enter'||e.key===' ')){e.preventDefault();setSelectedCode(code);}}}><title>{f.properties?.name??code}{has?` · ${pct(analyticsMap.get(code)?.market_cap_weighted_return)}`:' · No analytics available'}</title></path>;
     })}</g></svg><div className="map-zoom"><button onClick={()=>setZoom(v=>Math.min(1.8,v+.15))} aria-label="Zoom in">+</button><button onClick={()=>setZoom(v=>Math.max(.85,v-.15))} aria-label="Zoom out">−</button></div><div className="map-legend"><span>LOSS</span><i className="legend-loss"/><i className="legend-flat"/><i className="legend-gain"/><span>GAIN</span></div><div className="map-selection-hint"><Info size={12}/> Select a country to inspect market coverage</div></div>
     <div className="map-footnote">Country colours represent market-cap-weighted return where analytics exist. Grey indicates no available country analytics.</div>
    </section>
    <aside className="world-side-panel"><div className="leaderboard-heading"><div><strong>COUNTRY LEADERBOARD</strong><small>{region==='All regions'?'Global ranking':region}</small></div><span className="ranking-badge">1D</span></div>
     <div className="leaderboard-summary"><div><strong>{rows.length}</strong><small>ANALYTICS</small></div><div><strong className="positive-number">{rows.filter(x=>(x.market_cap_weighted_return??0)>0).length}</strong><small>GAINING</small></div><div><strong className="negative-number">{rows.filter(x=>(x.market_cap_weighted_return??0)<0).length}</strong><small>LOSING</small></div></div>
     <div className="leader-section"><div className="leader-label positive-label">TOP GAINERS</div>{gainers.length?gainers.map((x,i)=><button className={selectedCode===x.country_code?'leader-row chosen':'leader-row'} key={x.country_code} onClick={()=>setSelectedCode(x.country_code)}><span className="leader-rank">{i+1}</span><span className="leader-country"><b>{x.country_code}</b><small>{x.country_name}</small></span><strong className="positive-number"><ArrowUpRight size={12}/>{pct(x.market_cap_weighted_return)}</strong></button>):<div className="leader-empty">No positive returns available</div>}</div>
     <div className="leader-section"><div className="leader-label negative-label">TOP LOSERS</div>{losers.length?losers.map((x,i)=><button className={selectedCode===x.country_code?'leader-row chosen':'leader-row'} key={x.country_code} onClick={()=>setSelectedCode(x.country_code)}><span className="leader-rank">{i+1}</span><span className="leader-country"><b>{x.country_code}</b><small>{x.country_name}</small></span><strong className="negative-number"><ArrowDownRight size={12}/>{pct(x.market_cap_weighted_return)}</strong></button>):<div className="leader-empty">No negative returns available</div>}</div>
    </aside>
   </div>
   <section className="country-detail-panel">{selectedCode?<><div className="country-detail-title"><div><span className="detail-kicker">SELECTED COUNTRY</span><h2>{selectedRegistry?.name??selectedCode}</h2><p>{selectedCode} · {selectedRegistry?.currency??'Currency unavailable'} · {selectedRegistry?.timezone??'Timezone unavailable'}</p></div><button onClick={()=>setSelectedCode(null)}>Clear selection</button></div>{detailQuery.isLoading?<LoadingState label="Loading country overview"/>:detailQuery.isError?<div className="country-detail-unavailable">Country registry is available, but detailed analytics could not be loaded.</div>:detailQuery.data?<><div className="country-detail-metrics"><div><small>MARKET-CAP WEIGHTED RETURN</small><strong className={(detailQuery.data.market_cap_weighted_return??0)>=0?'positive-number':'negative-number'}>{pct(detailQuery.data.market_cap_weighted_return)}</strong></div><div><small>EQUAL-WEIGHTED RETURN</small><strong>{pct(detailQuery.data.equal_weighted_return)}</strong></div><div><small>TRACKED COMPANIES</small><strong>{detailQuery.data.tracked_companies.toLocaleString()}</strong></div><div><small>VALID OBSERVATIONS</small><strong>{(detailQuery.data.breadth.valid_observation_count ?? 0).toLocaleString()}</strong></div><div><small>MARKET CAP</small><strong>{detailQuery.data.total_market_cap==null?'—':formatCompact(detailQuery.data.total_market_cap)}</strong></div></div><div className="country-exchange-list"><small>REGISTERED EXCHANGES · {exchangesQuery.data?.length ?? 0}</small>{exchangesQuery.isLoading?<span>Loading exchange registry…</span>:exchangesQuery.data?.length?exchangesQuery.data.map(exchange=><span key={exchange.id}>{exchange.code} · {exchange.name}</span>):<span>No exchanges registered for this country</span>}</div></>:<div className="country-detail-unavailable">No country analytics are available for this selection.</div>}</>:<div className="country-detail-empty"><MapPinned size={18}/><div><strong>Country details</strong><span>Choose a country on the map or leaderboard to view its available analytics and registry information.</span></div></div>}</section>
   <div className="world-data-note"><Info size={13}/> Country analytics use the backend's current 1-day observation calculation. This view does not claim real-time market streaming.</div>
  </>}
 </div>;
}
