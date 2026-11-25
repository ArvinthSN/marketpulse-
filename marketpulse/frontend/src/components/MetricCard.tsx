import type { ReactNode } from 'react';

export function MetricCard({ label, value, detail, icon, accent = 'blue' }: { label: string; value: string; detail?: string; icon: ReactNode; accent?: 'blue' | 'green' | 'amber' | 'purple' }) {
  return <article className="metric-card">
    <div className="metric-top"><span>{label}</span><span className={`metric-icon icon-${accent}`}>{icon}</span></div>
    <strong className="metric-value">{value}</strong>
    {detail && <span className="metric-detail">{detail}</span>}
  </article>;
}
