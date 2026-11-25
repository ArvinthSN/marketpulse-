export type DataStatus = 'AVAILABLE' | 'PARTIAL' | 'STALE' | 'UNAVAILABLE' | 'LIVE' | 'DELAYED' | 'SNAPSHOT';

export interface Breadth {
  advancing: number;
  declining: number;
  unchanged: number;
  advance_decline_ratio?: number | null;
  advance_decline_difference?: number;
  valid_observation_count?: number;
}

export interface GlobalOverview {
  market: string;
  period: string;
  reporting_currency: string;
  calculated_at: string;
  data_status: DataStatus;
  tracked_companies: number;
  active_exchanges: number;
  market_breadth: Breadth;
}

export interface CountryOverview {
  country_code: string;
  country_name: string;
  reporting_currency: string;
  market_cap_weighted_return: number | null;
  equal_weighted_return: number | null;
  total_market_cap: number | null;
  tracked_companies: number;
  breadth: Breadth;
  data_status?: DataStatus;
  source_observation_at?: string | null;
  coverage?: { expected: number; available: number; missing: number };
}

export interface SectorOverview {
  sector_id: number;
  sector_name: string;
  reporting_currency: string;
  market_cap_weighted_return: number | null;
  equal_weighted_return: number | null;
  total_market_cap: number | null;
  total_volume: number | null;
  listed_companies: number;
  valid_companies: number;
  breadth: Breadth;
}

export interface CountryMover {
  company_id: number;
  name: string;
  return_percentage: number;
}

export interface CompanyPerformance {
  company_id: number;
  symbol: string;
  currency: string;
  reporting_currency: string;
  performance: Record<string, number | null>;
  price_basis: 'adjusted' | 'unadjusted';
  data_quality: {
    data_status: DataStatus;
    source: string;
    last_market_observation: string | null;
    calculated_at: string;
    is_stale: boolean;
    coverage: { expected: number; available: number; missing: number };
    warnings: string[];
  };
}

export interface CompanyHistory { timestamp: string; open: number; high: number; low: number; close: number; volume: number; currency: string; }

export interface Company {
  id: number;
  name: string;
  short_name?: string | null;
  country_code?: string | null;
  sector_id?: number | null;
  market_cap?: number | null;
  shares_outstanding?: number | null;
  website?: string | null;
}

export interface Country {
  id: number;
  code: string;
  name: string;
  currency: string;
  timezone: string;
}

export interface Exchange {
  id: number;
  code: string;
  name: string;
  country_code: string;
  currency: string;
  timezone: string;
  enabled: boolean;
}

export interface Quote {
  symbol: string;
  exchange: string;
  price: number;
  previous_close?: number | null;
  change?: number | null;
  change_percentage?: number | null;
  volume?: number | null;
  currency: string;
  source: string;
  market_timestamp: string;
  received_at: string;
  data_status: DataStatus;
  data_delay_seconds?: number;
}
