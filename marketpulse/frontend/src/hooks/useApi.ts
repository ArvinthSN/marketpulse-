import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';

export function useGlobalOverview(period: string) {
  return useQuery({ queryKey: ['global-overview', period], queryFn: ({ signal }) => api.globalOverview(period, signal), refetchInterval: 60_000 });
}

export function useCountries() {
  return useQuery({ queryKey: ['countries'], queryFn: ({ signal }) => api.countries(signal) });
}

export function useSectors() {
  return useQuery({ queryKey: ['sectors'], queryFn: ({ signal }) => api.sectors(signal), refetchInterval: 60_000 });
}
