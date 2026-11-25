import { AlertCircle, LoaderCircle, RefreshCw } from 'lucide-react';

export function LoadingState({ label = 'Loading market data' }: { label?: string }) {
  return <div className="state-view"><LoaderCircle className="spin" size={22} /><span>{label}</span></div>;
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return <div className="state-view state-error"><AlertCircle size={22} /><div><strong>Unable to load data</strong><p>{message}</p>{onRetry && <button className="text-button" onClick={onRetry}><RefreshCw size={14} /> Try again</button>}</div></div>;
}

export function EmptyState({ title, description }: { title: string; description: string }) {
  return <div className="empty-state"><strong>{title}</strong><p>{description}</p></div>;
}
