import { fetchAPI } from '@/lib/api';

type Heat = { iso: string; name: string; risk_score: number; bucket: string; wow_change: number };

export default async function PortfolioPage() {
  const heat = await fetchAPI<Heat[]>('/global/heatmap');
  const pick = heat.slice(0, 3);
  const total = pick.reduce((s, x) => s + x.risk_score, 0) || 1;
  const weighted = pick.reduce((s, x) => s + x.risk_score * (x.risk_score / total), 0);
  return (
    <div className="card">
      <h2>Portfolio Exposure View (Demo)</h2>
      <p>Example weighted portfolio risk: <strong>{weighted.toFixed(1)}</strong></p>
      <ul>
        {pick.map((c) => (
          <li key={c.iso}>{c.name} ({c.iso}) · score {c.risk_score}</li>
        ))}
      </ul>
      <p>Stress scenarios available in API-ready architecture: oil +20%, rates +200bps, FX shock, trade shock.</p>
    </div>
  );
}
