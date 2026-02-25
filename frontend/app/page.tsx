import Link from 'next/link';

import { WorldRiskMap } from '@/components/WorldRiskMap';
import { fetchApi } from '@/lib/api';

type HeatmapPoint = {
  iso: string;
  name: string;
  risk_score: number;
  bucket: string;
  weekly_delta: number;
  black_swan_signal: boolean;
};

type BlackSwanEvent = {
  iso: string;
  name: string;
  risk_score: number;
  weekly_delta: number;
  zscore_delta: number;
};

export default async function HomePage() {
  const [heatmap, blackSwans] = await Promise.all([
    fetchApi<HeatmapPoint[]>('/global/heatmap'),
    fetchApi<BlackSwanEvent[]>('/global/black-swans'),
  ]);

  const topDeteriorations = [...heatmap].sort((a, b) => b.weekly_delta - a.weekly_delta).slice(0, 10);
  const topRisk = [...heatmap].sort((a, b) => b.risk_score - a.risk_score).slice(0, 10);

  return (
    <div className="grid">
      <div className="card">
        <h2>World Risk Overview</h2>
        <p>Χάρτης παγκόσμιου ρίσκου για χώρες κοντά ή μέσα σε κρίση.</p>
        <WorldRiskMap data={heatmap} />
      </div>

      <div className="card">
        <h3>Top Risk Countries (chart)</h3>
        {topRisk.map((row) => (
          <div key={row.iso} style={{ marginBottom: 10 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
              <span>{row.name}</span>
              <span>{row.risk_score.toFixed(1)}</span>
            </div>
            <div style={{ background: '#e2e8f0', borderRadius: 999, height: 8 }}>
              <div style={{ width: `${Math.min(row.risk_score, 100)}%`, height: 8, borderRadius: 999, background: '#dc2626' }} />
            </div>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>Biggest Weekly Deteriorations</h3>
        <table>
          <thead>
            <tr><th>Country</th><th>Risk Score</th><th>Δ 7d</th><th>Bucket</th><th>Black Swan</th></tr>
          </thead>
          <tbody>
            {topDeteriorations.map((row) => (
              <tr key={row.iso}>
                <td><Link href={`/country/${row.iso}`}>{row.name}</Link></td>
                <td>{row.risk_score}</td>
                <td>{row.weekly_delta}</td>
                <td>{row.bucket}</td>
                <td>{row.black_swan_signal ? '⚠️' : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3>Potential Black Swan Events</h3>
        {blackSwans.length === 0 ? (
          <p>No extreme cross-country anomaly this cycle.</p>
        ) : (
          <table>
            <thead><tr><th>Country</th><th>Risk</th><th>Δ 7d</th><th>Z-score</th></tr></thead>
            <tbody>
              {blackSwans.map((event) => (
                <tr key={event.iso}>
                  <td>{event.name}</td>
                  <td>{event.risk_score}</td>
                  <td>{event.weekly_delta}</td>
                  <td>{event.zscore_delta}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
