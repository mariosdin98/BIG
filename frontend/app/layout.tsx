import './globals.css';
import Link from 'next/link';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="container">
          <h1>Crisis Radar</h1>
          <p>Early warning platform for recession & crisis risk by country.</p>
          <nav style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
            <Link href="/">Global</Link>
            <Link href="/alerts">Alerts</Link>
            <Link href="/portfolio">Portfolio</Link>
          </nav>
          {children}
        </div>
      </body>
    </html>
  );
}
