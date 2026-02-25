export default function PortfolioPage() {
  return (
    <div className="card">
      <h2>Portfolio Exposure</h2>
      <p>Use POST /portfolio and GET /portfolio/{'{id}'}/risk endpoints to integrate weighted risk monitoring in your OMS.</p>
      <p>Scenario stress tests (oil +20%, rates +200bps, FX shock, trade shock) can be plugged into this page in the next sprint.</p>
    </div>
  );
}
