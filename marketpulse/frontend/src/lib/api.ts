import type { Company, CompanyPerformance, Country, CountryOverview, Exchange, GlobalOverview, SectorOverview, Quote } from '../types/market';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

export class ApiError extends Error {
  constructor(message: string, readonly status: number) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      signal,
      headers: { Accept: 'application/json' }
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') throw error;
    throw new ApiError('Unable to reach MARKETPULSE API. Check that the backend is running.', 0);
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: unknown } | null;
    const message = typeof body?.detail === 'string' ? body.detail : `Request failed (${response.status})`;
    throw new ApiError(message, response.status);
  }
  return response.json() as Promise<T>;
}

export const api = {
  globalOverview: (period = '1D', signal?: AbortSignal) =>
    request<GlobalOverview>(`/api/v1/analytics/global/overview?period=${encodeURIComponent(period)}`, signal),
  countries: (signal?: AbortSignal) => request<Country[]>('/api/v1/countries', signal),
  globalCountries: (signal?: AbortSignal) => request<CountryOverview[]>('/api/v1/analytics/global/countries', signal),
  exchanges: (country?: string, signal?: AbortSignal) =>
    request<Exchange[]>(`/api/v1/exchanges${country ? `?country=${encodeURIComponent(country)}` : ''}`, signal),
  countryOverview: (code: string, signal?: AbortSignal) =>
    request<CountryOverview>(`/api/v1/analytics/countries/${encodeURIComponent(code)}/overview`, signal),
  sectors: (signal?: AbortSignal) =>
    request<SectorOverview[]>('/api/v1/analytics/global/sectors', signal),
  sectorOverview: (id: number, signal?: AbortSignal) =>
    request<SectorOverview>(`/api/v1/analytics/sectors/${id}/overview`, signal),
  companies: (params: { country?: string; limit?: number; offset?: number } = {}, signal?: AbortSignal) => {
    const query = new URLSearchParams();
    if (params.country) query.set('country', params.country);
    query.set('limit', String(params.limit ?? 100));
    query.set('offset', String(params.offset ?? 0));
    return request<Company[]>(`/api/v1/companies?${query.toString()}`, signal);
  },
  companyPerformance: (id: number, period = '1D', signal?: AbortSignal) =>
    request<CompanyPerformance>(`/api/v1/analytics/companies/${id}/performance?period=${encodeURIComponent(period)}`, signal),
  quote: (symbol: string, exchange = 'NASDAQ', signal?: AbortSignal) =>
    request<Quote>(`/api/v1/market/quotes/${encodeURIComponent(symbol)}?exchange=${encodeURIComponent(exchange)}`, signal)
};
