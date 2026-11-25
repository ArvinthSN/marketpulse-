import type { DataStatus } from '../types/market';

const labels: Record<DataStatus, string> = {
  AVAILABLE: 'Available', PARTIAL: 'Partial coverage', STALE: 'Stale',
  UNAVAILABLE: 'Unavailable', LIVE: 'Live', DELAYED: 'Delayed', SNAPSHOT: 'Snapshot'
};

export function StatusPill({ status }: { status: DataStatus }) {
  return <span className={`status-pill status-${status.toLowerCase()}`}><span className="status-dot" />{labels[status] ?? status}</span>;
}
