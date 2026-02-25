import { fetchApi } from '@/lib/api';

type CountryLatest = {
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
  const latest = await fetchApi<CountryLatest>(`/countries/${params.iso}/latest`);

  return (
    <div className="grid">
      <div className="card">
        <h2>{latest.country} Country Profile</h2>
        <div className="metric">Risk Score: {latest.risk_score} ({latest.bucket})</div>
        <p>Recession probability 6m: {Math.round(latest.prob_recession_6m * 100)}%</p>
        <p>Recession probability 12m: {Math.round(latest.prob_recession_12m * 100)}%</p>
      </div>

      <div className="card">
        <h3>Subindices</h3>
        <table><tbody>
          {Object.entries(latest.subindices).map(([k, v]) => (
            <tr key={k}><td>{k}</td><td>{v}</td></tr>
          ))}
        </tbody></table>
      </div>

      <div className="card">
        <h3>Top Drivers (Explainability)</h3>
        <ul>
          {latest.drivers.map((d) => <li key={d.feature}>{d.feature}: {d.impact}</li>)}
        </ul>
      </div>
    </div>
  );
}
