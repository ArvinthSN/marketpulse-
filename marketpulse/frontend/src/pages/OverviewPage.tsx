import { useMemo, useState } from 'react';
import { ArrowDownRight, ArrowUpRight, BarChart3, Building2, Globe2, RefreshCw, ShieldCheck, TrendingUp } from 'lucide-react';
import { useGlobalOverview, useCountries, useSectors } from '../hooks/useApi';
import { MetricCard } from '../components/MetricCard';
import { SectionHeader } from '../components/SectionHeader';
import { LoadingState, ErrorState, EmptyState } from '../components/StateView';
import { StatusPill } from '../components/StatusPill';
import { formatCompact, formatDate, formatNumber, formatPercent } from '../lib/format';
import type { CountryOverview, SectorOverview } from '../types/market';

const periods = ['1D', '1W', '1M', '3M', '6M', 'YTD', '1Y'];

function ReturnValue({ value }: { value: number | null | undefined }) {
  const positive = (value ?? 0) >= 0;
  return <span className={value == null ? 'return-neutral' : positive ? 'return-positive' : 'return-negative'}>{value == null ? '—' : <>{positive ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}{formatPercent(value)}</>}</span>;
}

export function OverviewPage() {
  const [period, setPeriod] = useState('1D');
  const overview = useGlobalOverview(period);
  const countries = useCountries();
  const sectors = useSectors();

  const countryRows = useMemo(() => (countries.data ?? []).map(country => ({
    ...country,
    overview: undefined as CountryOverview | undefined
  })), [countries.data]);

  return <div className="dashboard-page">
    <div className="page-heading">
      <div><div className="eyebrow">MARKET OVERVIEW <span className="eyebrow-line" /></div><h1>Global markets, <em>in focus.</em></h1><p>Explore global market structure, country coverage and sector-level intelligence.</p></div>
      <div className="heading-meta"><span className="meta-label">ANALYTICS PERIOD</span><div className="period-control">{periods.map(item => <button key={item} onClick={() => setPeriod(item)} className={period === item ? 'selected' : ''}>{item}</button>)}</div></div>
    </div>

    {overview.isLoading ? <LoadingState label="Loading global market overview" /> : overview.isError ? <ErrorState message={overview.error.message} onRetry={() => void overview.refetch()} /> : overview.data && <>
      <div className="overview-status"><StatusPill status={overview.data.data_status} /><span>Calculated {formatDate(overview.data.calculated_at)}</span><button onClick={() => void overview.refetch()} className="refresh-button"><RefreshCw size={13} /> Refresh</button></div>
      <div className="metrics-grid">
        <MetricCard label="TRACKED COMPANIES" value={formatNumber(overview.data.tracked_companies)} detail="In configured instrument universe" icon={<Building2 size={18} />} accent="blue" />
        <MetricCard label="ACTIVE EXCHANGES" value={formatNumber(overview.data.active_exchanges)} detail="Represented in company universe" icon={<Globe2 size={18} />} accent="purple" />
        <MetricCard label="ADVANCING" value={formatNumber(overview.data.market_breadth?.advancing)} detail="Companies with positive return" icon={<TrendingUp size={18} />} accent="green" />
        <MetricCard label="DECLINING" value={formatNumber(overview.data.market_breadth?.declining)} detail="Companies with negative return" icon={<BarChart3 size={18} />} accent="amber" />
      </div>
      <div className="data-notice"><ShieldCheck size={16} /><span>Analytics use persisted historical observations. Values are not represented as live quotes.</span><span className="notice-period">{period} VIEW</span></div>
    </>}

    <div className="content-grid">
      <section className="panel countries-panel">
        <SectionHeader title="Market coverage" description="Countries configured in the exchange registry" action={<span className="panel-count">{countries.data?.length ?? 0} COUNTRIES</span>} />
        {countries.isLoading ? <LoadingState label="Loading country registry" /> : countries.isError ? <ErrorState message={countries.error.message} onRetry={() => void countries.refetch()} /> : countries.data?.length ? <div className="country-list">{countryRows.map(country => <div className="country-row" key={country.code}><div className="country-identity"><span className="country-code">{country.code}</span><div><strong>{country.name}</strong><small>{country.currency} · {country.timezone}</small></div></div><span className="registry-label">Registry</span></div>)}</div> : <EmptyState title="No countries configured" description="Import your country and exchange registry to populate this view." />}
      </section>
      <section className="panel breadth-panel">
        <SectionHeader title="Market breadth" description="Observed company advances and declines" />
        {overview.data ? <div className="breadth-content">
          <div className="breadth-stat"><span>Advancers</span><strong className="positive-number">{formatNumber(overview.data.market_breadth.advancing)}</strong></div>
          <div className="breadth-bar"><span style={{ width: `${overview.data.market_breadth.valid_observation_count ? overview.data.market_breadth.advancing / overview.data.market_breadth.valid_observation_count * 100 : 0}%` }} /></div>
          <div className="breadth-stat"><span>Decliners</span><strong className="negative-number">{formatNumber(overview.data.market_breadth.declining)}</strong></div>
          <div className="breadth-stat"><span>Unchanged</span><strong>{formatNumber(overview.data.market_breadth.unchanged)}</strong></div>
          <div className="breadth-footer"><span>Valid observations</span><strong>{formatNumber(overview.data.market_breadth.valid_observation_count)}</strong></div>
        </div> : <EmptyState title="Breadth unavailable" description="Market breadth will appear when historical observations are available." />}
      </section>
    </div>

    <section className="panel sectors-panel">
      <SectionHeader title="Sector intelligence" description="Sector performance computed from persisted company observations" action={<span className="panel-count">{sectors.data?.length ?? 0} SECTORS</span>} />
      {sectors.isLoading ? <LoadingState label="Loading sector analytics" /> : sectors.isError ? <ErrorState message={sectors.error.message} onRetry={() => void sectors.refetch()} /> : sectors.data?.length ? <div className="sector-grid">{sectors.data.map((sector: SectorOverview) => <div className="sector-tile" key={sector.sector_id}>
        <div className="sector-tile-top"><span className="sector-indicator" /><span>{sector.valid_companies} / {sector.listed_companies} COVERED</span></div>
        <strong>{sector.sector_name}</strong>
        <ReturnValue value={sector.market_cap_weighted_return} />
        <div className="sector-subline">Equal weighted <b><ReturnValue value={sector.equal_weighted_return} /></b></div>
      </div>)}</div> : <EmptyState title="No sector analytics available" description="Sector results require classified companies with historical price observations." />}
    </section>

    <div className="dashboard-footer"><span>MARKETPULSE · GLOBAL MARKET INTELLIGENCE</span><span>API-backed · {overview.data?.reporting_currency ?? 'USD'} reporting context</span></div>
  </div>;
}
