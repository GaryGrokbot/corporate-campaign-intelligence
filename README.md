# Corporate Campaign Intelligence

Research database and API for animal advocacy campaign targeting. Tracks the top 20 animal agriculture companies worldwide with vulnerability analysis, campaign history, and key contacts.

## What's Inside

- **20 companies** — JBS, Tyson, Cargill, Smithfield, Hormel, Perdue, Pilgrim's Pride, and more
- **18+ documented campaigns** — environmental, legal, consumer, investor pressure, regulatory
- **Vulnerability analysis** — categorized by severity (critical/high/medium) across environmental, labor, governance, animal welfare, antitrust, and greenwashing dimensions
- **Key contacts** — publicly available leadership info

All data sourced from publicly available information: Wikipedia, SEC filings, sustainability reports, news coverage, NGO investigations, and court records.

## Quick Start

```bash
pip install -r requirements.txt
python -m db.seed          # Initialize SQLite database
uvicorn api.main:app --port 8003
```

## Docker

```bash
docker build -t campaign-intel .
docker run -p 8003:8003 campaign-intel
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API info and stats |
| `GET /companies` | Search companies (params: `q`, `industry`, `animal_product`, `min_revenue`) |
| `GET /companies/{id}/profile` | Full company profile with campaigns and contacts |
| `GET /companies/{id}/vulnerabilities` | Vulnerability report for campaign targeting |
| `GET /campaigns` | Browse campaigns (params: `campaign_type`, `status`, `organizer`) |

## Example Queries

```bash
# Search for beef companies
curl "localhost:8003/companies?animal_product=beef"

# Get Tyson's vulnerability report
curl "localhost:8003/companies/2/vulnerabilities"

# Find active environmental campaigns
curl "localhost:8003/campaigns?campaign_type=environmental&status=active"

# Companies with revenue over $50B
curl "localhost:8003/companies?min_revenue=50"
```

## Data Sources

- Company financials: Wikipedia, SEC EDGAR, annual reports
- Vulnerabilities: NGO reports (Greenpeace, Mighty Earth, Mercy For Animals, HSUS, Amnesty International), news coverage, court filings
- Campaigns: Public advocacy records, news archives, legal databases
- Contacts: Public corporate disclosures, press releases

## Disclaimer

This tool aggregates publicly available information for research purposes. Verify all data before use in advocacy campaigns. Revenue figures use most recent available data (noted by year).

## License

MIT
