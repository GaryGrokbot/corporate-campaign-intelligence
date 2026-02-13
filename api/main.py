"""Corporate Campaign Intelligence API — research tool for animal advocacy."""
import json
import os
import sqlite3
from contextlib import contextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(
    title="Corporate Campaign Intelligence API",
    description="Research database and API for animal advocacy campaign targeting. "
    "All data sourced from publicly available information: SEC filings, "
    "sustainability reports, news coverage, and documented campaigns.",
    version="1.0.0",
)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "intel.db")


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _ensure_db():
    if not os.path.exists(DB_PATH):
        from db.seed import init_db
        init_db(DB_PATH)


def _row_to_dict(row):
    d = dict(row)
    for key in ("sustainability_claims", "vulnerabilities", "controversies"):
        if key in d and d[key]:
            try:
                d[key] = json.loads(d[key])
            except (json.JSONDecodeError, TypeError):
                pass
    return d


@app.on_event("startup")
async def startup():
    _ensure_db()


# ──────────────────────────────────────────────
# GET /companies — searchable list
# ──────────────────────────────────────────────
@app.get("/companies")
async def list_companies(
    q: Optional[str] = Query(None, description="Search by name or industry"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    animal_product: Optional[str] = Query(None, description="Filter by animal product (e.g. beef, pork, chicken, dairy, eggs)"),
    min_revenue: Optional[float] = Query(None, description="Minimum revenue in USD billions"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List and search companies in the database."""
    conditions = []
    params = []

    if q:
        conditions.append("(name LIKE ? OR industry LIKE ? OR animal_products LIKE ?)")
        params.extend([f"%{q}%"] * 3)
    if industry:
        conditions.append("industry LIKE ?")
        params.append(f"%{industry}%")
    if animal_product:
        conditions.append("animal_products LIKE ?")
        params.append(f"%{animal_product}%")
    if min_revenue is not None:
        conditions.append("revenue_usd_billions >= ?")
        params.append(min_revenue)

    where = " WHERE " + " AND ".join(conditions) if conditions else ""

    with get_db() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM companies{where}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT id, name, ticker, industry, headquarters, revenue_usd_billions, revenue_year, employees, animal_products, website "
            f"FROM companies{where} ORDER BY revenue_usd_billions DESC NULLS LAST LIMIT ? OFFSET ?",
            params + [limit, offset],
        ).fetchall()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "companies": [dict(r) for r in rows],
    }


# ──────────────────────────────────────────────
# GET /companies/{id}/profile — full company profile
# ──────────────────────────────────────────────
@app.get("/companies/{company_id}/profile")
async def company_profile(company_id: int):
    """Get full profile for a company including campaigns and contacts."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM companies WHERE id = ?", (company_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Company not found")

        campaigns = conn.execute(
            "SELECT * FROM campaigns WHERE company_id = ? ORDER BY start_year DESC", (company_id,)
        ).fetchall()

        contacts = conn.execute(
            "SELECT * FROM contacts WHERE company_id = ?", (company_id,)
        ).fetchall()

    company = _row_to_dict(row)
    return {
        "company": company,
        "campaigns": [dict(c) for c in campaigns],
        "contacts": [dict(c) for c in contacts],
    }


# ──────────────────────────────────────────────
# GET /companies/{id}/vulnerabilities — focused vulnerability report
# ──────────────────────────────────────────────
@app.get("/companies/{company_id}/vulnerabilities")
async def company_vulnerabilities(company_id: int):
    """Get vulnerability analysis for campaign targeting."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, name, vulnerabilities, controversies, sustainability_claims FROM companies WHERE id = ?",
            (company_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Company not found")

        campaigns = conn.execute(
            "SELECT campaign_type, campaign_name, organizer, status, outcome FROM campaigns WHERE company_id = ?",
            (company_id,),
        ).fetchall()

    company = _row_to_dict(row)
    vulns = company.get("vulnerabilities", [])
    controversies = company.get("controversies", [])
    claims = company.get("sustainability_claims", [])

    # Categorize vulnerabilities by severity
    by_severity = {"critical": [], "high": [], "medium": [], "low": []}
    for v in vulns:
        sev = v.get("severity", "medium")
        by_severity.setdefault(sev, []).append(v)

    return {
        "company_id": company["id"],
        "company_name": company["name"],
        "vulnerabilities_by_severity": {k: v for k, v in by_severity.items() if v},
        "total_vulnerabilities": len(vulns),
        "controversies": controversies,
        "sustainability_claims_to_scrutinize": claims,
        "existing_campaigns": [dict(c) for c in campaigns],
    }


# ──────────────────────────────────────────────
# GET /campaigns — all campaigns, filterable
# ──────────────────────────────────────────────
@app.get("/campaigns")
async def list_campaigns(
    campaign_type: Optional[str] = Query(None, description="Filter: investor_pressure, regulatory, consumer, media, legal, shareholder_resolution, environmental, labor"),
    status: Optional[str] = Query(None, description="Filter: active, completed, planned, unknown"),
    organizer: Optional[str] = Query(None, description="Search by organizing group"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List advocacy campaigns with filters."""
    conditions = []
    params = []

    if campaign_type:
        conditions.append("c.campaign_type = ?")
        params.append(campaign_type)
    if status:
        conditions.append("c.status = ?")
        params.append(status)
    if organizer:
        conditions.append("c.organizer LIKE ?")
        params.append(f"%{organizer}%")

    where = " WHERE " + " AND ".join(conditions) if conditions else ""

    with get_db() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM campaigns c{where}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT c.*, co.name as company_name FROM campaigns c "
            f"JOIN companies co ON c.company_id = co.id{where} "
            f"ORDER BY c.start_year DESC NULLS LAST LIMIT ? OFFSET ?",
            params + [limit, offset],
        ).fetchall()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "campaigns": [dict(r) for r in rows],
    }


# ──────────────────────────────────────────────
# Root
# ──────────────────────────────────────────────
@app.get("/")
async def root():
    with get_db() as conn:
        company_count = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
        campaign_count = conn.execute("SELECT COUNT(*) FROM campaigns").fetchone()[0]
    return {
        "name": "Corporate Campaign Intelligence API",
        "version": "1.0.0",
        "description": "Research database for animal advocacy campaign targeting",
        "data": {
            "companies": company_count,
            "campaigns": campaign_count,
        },
        "endpoints": [
            "GET /companies — searchable company list",
            "GET /companies/{id}/profile — full company profile",
            "GET /companies/{id}/vulnerabilities — vulnerability analysis",
            "GET /campaigns — advocacy campaign database",
        ],
        "disclaimer": "All data sourced from publicly available information.",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
