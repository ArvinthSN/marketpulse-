import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface WatchlistState {
  companyIds: number[];
  add: (id: number) => void;
  remove: (id: number) => void;
  has: (id: number) => boolean;
}

export const useWatchlist = create<WatchlistState>()(persist((set, get) => ({
  companyIds: [],
  add: (id) => set((state) => ({ companyIds: state.companyIds.includes(id) ? state.companyIds : [...state.companyIds, id] })),
  remove: (id) => set((state) => ({ companyIds: state.companyIds.filter((item) => item !== id) })),
  has: (id) => get().companyIds.includes(id)
}), { name: 'marketpulse-watchlist-v1', partialize: (state) => ({ companyIds: state.companyIds }) }));
