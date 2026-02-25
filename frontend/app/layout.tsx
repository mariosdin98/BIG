import './styles.css';
import Link from 'next/link';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="topbar">
          <h1>Crisis Radar</h1>
          <nav>
            <Link href="/">Global</Link>
            <Link href="/alerts">Alerts</Link>
            <Link href="/portfolio">Portfolio</Link>
          </nav>
        </header>
        <main className="container">{children}</main>
      </body>
    </html>
  );
}
