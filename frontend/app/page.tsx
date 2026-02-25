import Link from 'next/link';
import { fetchAPI } from '@/lib/api';

type Heat = { iso: string; name: string; risk_score: number; bucket: string; wow_change: number };

function color(score: number): string {
  if (score >= 80) return '#8b1e1e';
  if (score >= 65) return '#92400e';
  if (score >= 45) return '#6b5e14';
  return '#14532d';
}

export default async function Home() {
  const heat = await fetchAPI<Heat[]>('/global/heatmap');

  return (
    <div className="grid" style={{ gap: 20 }}>
      <div className="card">
        <h2>Global Risk Heatmap</h2>
        <div className="map">
          {heat.map((c) => (
            <Link key={c.iso} href={`/countries/${c.iso}`} className="map-cell" style={{ background: color(c.risk_score) }}>
              <div><strong>{c.iso}</strong> · {c.name}</div>
              <div>Risk: {c.risk_score}</div>
              <div>WoW: {c.wow_change > 0 ? '+' : ''}{c.wow_change}</div>
            </Link>
          ))}
        </div>
      </div>

      <div className="card">
        <h2>Biggest Deteriorations</h2>
        <table className="table">
          <thead><tr><th>Country</th><th>Risk</th><th>Bucket</th><th>WoW</th></tr></thead>
          <tbody>
            {[...heat].sort((a, b) => b.wow_change - a.wow_change).map((c) => (
              <tr key={c.iso}>
                <td><Link href={`/countries/${c.iso}`}>{c.name}</Link></td>
                <td>{c.risk_score}</td>
                <td><span className={`badge ${c.bucket}`}>{c.bucket}</span></td>
                <td>{c.wow_change > 0 ? '+' : ''}{c.wow_change}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
