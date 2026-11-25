import { Construction } from 'lucide-react';
export function PlaceholderPage({ title, description }: { title: string; description: string }) {
  return <div className="placeholder-page"><div className="placeholder-icon"><Construction size={24} /></div><div className="eyebrow">PHASE 4 · IN PROGRESS</div><h1>{title}</h1><p>{description}</p><span>This section will be enabled as its backend integration is completed.</span></div>;
}
