import { fetchApi } from '@/lib/api';

type Alert = {
  id: number;
  country_iso: string;
  severity: string;
  message: string;
  created_at: string;
};

export default async function AlertsPage() {
  const alerts = await fetchApi<Alert[]>('/alerts');

  return (
    <div className="card">
      <h2>Alerts Feed</h2>
      {alerts.length === 0 ? <p>No alerts yet. Add rules and run scheduled checks.</p> : (
        <table>
          <thead><tr><th>Country</th><th>Severity</th><th>Message</th><th>At</th></tr></thead>
          <tbody>{alerts.map((a) => <tr key={a.id}><td>{a.country_iso}</td><td>{a.severity}</td><td>{a.message}</td><td>{a.created_at}</td></tr>)}</tbody>
        </table>
      )}
    </div>
  );
}
