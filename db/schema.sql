CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    ticker TEXT,
    industry TEXT NOT NULL,
    headquarters TEXT,
    revenue_usd_billions REAL,
    revenue_year INTEGER,
    employees INTEGER,
    animal_products TEXT NOT NULL,          -- comma-separated: beef, pork, chicken, seafood, dairy, eggs
    sustainability_claims TEXT,             -- JSON array of claims
    vulnerabilities TEXT,                   -- JSON array of vulnerability objects
    controversies TEXT,                     -- JSON array of known controversies
    website TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    campaign_type TEXT NOT NULL,            -- investor_pressure, regulatory, consumer, media, legal, shareholder_resolution
    campaign_name TEXT,
    organizer TEXT,                         -- organization running the campaign
    status TEXT DEFAULT 'unknown',          -- active, completed, planned, unknown
    start_year INTEGER,
    outcome TEXT,
    description TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    public_email TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
CREATE INDEX IF NOT EXISTS idx_companies_industry ON companies(industry);
CREATE INDEX IF NOT EXISTS idx_campaigns_company ON campaigns(company_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_type ON campaigns(campaign_type);
CREATE INDEX IF NOT EXISTS idx_contacts_company ON contacts(company_id);
