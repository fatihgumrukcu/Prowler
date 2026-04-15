PROJECT: Prowler

RULES FOR AI:

- Do NOT rewrite entire files unnecessarily
- Prefer minimal diff changes
- Do NOT scan entire project
- Only use provided files

ARCHITECTURE:

- scraper.py → data collection
- parser.py → data parsing
- exporter.py → CSV export

CONSTRAINTS:

- No new dependencies unless required
- Keep scraping logic stable
- Avoid breaking pagination