import { fetchAPI } from '@/lib/api';

type Alert = { id: string; country: string; date: string; severity: string; message: string };

export default async function AlertsPage() {
  const alerts = await fetchAPI<Alert[]>('/alerts');
  return (
    <div className="card">
      <h2>Alerts Feed</h2>
      <table className="table">
        <thead><tr><th>Date</th><th>Country</th><th>Severity</th><th>Message</th></tr></thead>
        <tbody>
          {alerts.map((a) => (
            <tr key={a.id}><td>{a.date}</td><td>{a.country}</td><td>{a.severity}</td><td>{a.message}</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
