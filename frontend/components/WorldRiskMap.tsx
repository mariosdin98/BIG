'use client';

import { ComposableMap, Geographies, Geography } from 'react-simple-maps';
import geography from 'world-atlas/countries-110m.json';

type HeatmapPoint = {
  iso: string;
  name: string;
  risk_score: number;
  bucket: string;
  weekly_delta: number;
  black_swan_signal: boolean;
};

function colorForScore(score: number): string {
  if (score >= 75) return '#b91c1c';
  if (score >= 50) return '#ea580c';
  if (score >= 25) return '#facc15';
  return '#16a34a';
}

export function WorldRiskMap({ data }: { data: HeatmapPoint[] }) {
  const byIso3 = Object.fromEntries(data.map((d) => [d.iso, d]));

  return (
    <div style={{ border: '1px solid #e5e7eb', borderRadius: 12, padding: 16 }}>
      <h3>Global Crisis Heatmap</h3>
      <ComposableMap projectionConfig={{ scale: 150 }} style={{ width: '100%', height: '480px' }}>
        <Geographies geography={geography as never}>
          {({ geographies }) =>
            geographies.map((geo) => {
              const entry = byIso3[geo.properties.iso_a3 as string];
              return (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill={entry ? colorForScore(entry.risk_score) : '#e5e7eb'}
                  stroke="#ffffff"
                  strokeWidth={0.5}
                  style={{ default: { outline: 'none' }, hover: { outline: 'none' }, pressed: { outline: 'none' } }}
                >
                  <title>
                    {entry
                      ? `${entry.name}: ${entry.risk_score} (${entry.bucket})${entry.black_swan_signal ? ' | Black Swan signal' : ''}`
                      : geo.properties.name}
                  </title>
                </Geography>
              );
            })
          }
        </Geographies>
      </ComposableMap>
    </div>
  );
}
