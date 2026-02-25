import { fetchAPI } from '@/lib/api';

type Country = {
  country: string;
  date: string;
  risk_score: number;
  bucket: string;
  prob_recession_6m: number;
  prob_recession_12m: number;
  subindices: Record<string, number>;
  drivers: { feature: string; impact: number }[];
};

export default async function CountryPage({ params }: { params: { iso: string } }) {
  const latest = await fetchAPI<Country>(`/countries/${params.iso}/latest`);
  const history = await fetchAPI<Country[]>(`/countries/${params.iso}/history`);

  return (
    <div className="grid">
      <div className="card">
        <h2>{latest.country} · Country Risk</h2>
        <p>Risk score: <strong>{latest.risk_score}</strong> · Bucket: <span className={`badge ${latest.bucket}`}>{latest.bucket}</span></p>
        <p>Recession probability: 6m <strong>{Math.round(latest.prob_recession_6m * 100)}%</strong> · 12m <strong>{Math.round(latest.prob_recession_12m * 100)}%</strong></p>
      </div>

      <div className="card">
        <h3>Subindices</h3>
        <div className="grid grid-3">
          {Object.entries(latest.subindices).map(([k, v]) => (
            <div key={k} className="card">
              <div>{k}</div>
              <strong>{v.toFixed(1)}</strong>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h3>Top Drivers</h3>
        <ul>
          {latest.drivers.map((d) => (
            <li key={d.feature}>{d.feature}: {d.impact}</li>
          ))}
        </ul>
      </div>

      <div className="card">
        <h3>24m Trend (risk score)</h3>
        <div style={{ display: 'flex', gap: 4, alignItems: 'flex-end', height: 100 }}>
          {history.map((h) => (
            <div key={h.date} title={`${h.date}: ${h.risk_score}`} style={{ width: 10, height: `${h.risk_score}%`, background: '#60a5fa' }} />
          ))}
        </div>
      </div>
    </div>
  );
}
