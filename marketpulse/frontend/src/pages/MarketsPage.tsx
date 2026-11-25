import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowRight, Search, Globe2 } from 'lucide-react';
import { api } from '../lib/api';
import { formatPercent } from '../lib/format';
import { ErrorState, LoadingState } from '../components/StateView';

export function MarketsPage() {
  const [search, setSearch] = useState('');
  const countriesQuery = useQuery({ queryKey: ['markets-country-registry'], queryFn: ({ signal }) => api.countries(signal) });
  const analyticsQuery = useQuery({ queryKey: ['markets-country-analytics'], queryFn: ({ signal }) => api.globalCountries(signal), refetchInterval: 60_000 });
  const analytics = useMemo(() => new Map((analyticsQuery.data ?? []).map(item => [item.country_code, item])), [analyticsQuery.data]);
  const countries = (countriesQuery.data ?? []).filter(country => `${country.name} ${country.code}`.toLowerCase().includes(search.toLowerCase()));
  const loading = countriesQuery.isLoading || analyticsQuery.isLoading;
  const error = countriesQuery.error ?? analyticsQuery.error;
  return <div className="markets-directory">
    <div className="eyebrow"><Globe2 size={12}/> GLOBAL MARKET DIRECTORY <span className="eyebrow-line"/></div>
    <div className="markets-directory-heading"><div><h1>Explore <em>markets.</em></h1><p>Choose a country to inspect its exchanges, market breadth, company performance and data coverage.</p></div><div className="markets-directory-count"><strong>{countries.length}</strong><span>REGISTERED COUNTRIES</span></div></div>
    <label className="markets-search"><Search size={16}/><input value={search} onChange={event => setSearch(event.target.value)} placeholder="Search by country name or ISO code"/></label>
    {error ? <ErrorState message={error.message} onRetry={() => { void countriesQuery.refetch(); void analyticsQuery.refetch(); }}/> : loading ? <LoadingState label="Loading configured country markets"/> : countries.length ? <div className="markets-country-grid">{countries.map(country => {
      const item = analytics.get(country.code);
      const value = item?.market_cap_weighted_return;
      return <Link className="markets-country-card" to={`/markets/${country.code}`} key={country.code}>
        <div className="markets-country-card-top"><span className="markets-country-code">{country.code}</span><ArrowRight size={15}/></div>
        <strong>{country.name}</strong><small>{country.currency} · {country.timezone}</small>
        <div className="markets-country-performance"><span>Market-cap weighted · 1D</span><b className={value == null ? '' : value > 0 ? 'positive-number' : value < 0 ? 'negative-number' : ''}>{value == null ? 'No analytics' : formatPercent(value)}</b></div>
        <div className="markets-country-foot"><span>{item?.tracked_companies ?? 0} tracked companies</span><span>{item?.data_status ?? 'REGISTRY ONLY'}</span></div>
      </Link>;
    })}</div> : <div className="country-inline-empty">No countries match your search.</div>}
    <div className="country-dashboard-footer">Country performance is sourced from persisted backend observations. A country without analytics remains unranked rather than being assigned a zero return.</div>
  </div>;
}
