"""Simple ingestion script for MVP public macro data.

Fetches GDP growth data from World Bank API for a few countries and prints latest values.
Can be adapted into scheduled ingestion.
"""

from __future__ import annotations

import httpx

COUNTRIES = ["USA", "GRC", "DEU", "JPN", "BRA"]


async def main() -> None:
    base = "https://api.worldbank.org/v2/country/{iso}/indicator/NY.GDP.MKTP.KD.ZG"
    async with httpx.AsyncClient(timeout=20) as client:
        for iso in COUNTRIES:
            resp = await client.get(base.format(iso=iso), params={"format": "json", "per_page": 5})
            resp.raise_for_status()
            payload = resp.json()[1]
            latest = next((row for row in payload if row.get("value") is not None), None)
            if latest:
                print(f"{iso}: GDP growth {latest['value']} ({latest['date']})")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
