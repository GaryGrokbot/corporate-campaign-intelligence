"""Seed the SQLite database with top 20 animal agriculture companies."""
import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "intel.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def init_db(db_path: str = None):
    db_path = db_path or DB_PATH
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())

    # Check if already seeded
    count = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    if count > 0:
        conn.close()
        return db_path

    companies = _get_companies()
    for c in companies:
        conn.execute(
            """INSERT INTO companies (name, ticker, industry, headquarters, revenue_usd_billions, revenue_year, employees, animal_products, sustainability_claims, vulnerabilities, controversies, website, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                c["name"], c.get("ticker"), c["industry"], c.get("headquarters"),
                c.get("revenue"), c.get("revenue_year"), c.get("employees"),
                c["animal_products"],
                json.dumps(c.get("sustainability_claims", [])),
                json.dumps(c.get("vulnerabilities", [])),
                json.dumps(c.get("controversies", [])),
                c.get("website"), c.get("notes"),
            ),
        )

    campaigns = _get_campaigns()
    for camp in campaigns:
        company_id = conn.execute(
            "SELECT id FROM companies WHERE name = ?", (camp["company"],)
        ).fetchone()
        if company_id:
            conn.execute(
                """INSERT INTO campaigns (company_id, campaign_type, campaign_name, organizer, status, start_year, outcome, description, source_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    company_id[0], camp["type"], camp.get("name"), camp.get("organizer"),
                    camp.get("status", "unknown"), camp.get("start_year"),
                    camp.get("outcome"), camp.get("description"), camp.get("source_url"),
                ),
            )

    contacts = _get_contacts()
    for ct in contacts:
        company_id = conn.execute(
            "SELECT id FROM companies WHERE name = ?", (ct["company"],)
        ).fetchone()
        if company_id:
            conn.execute(
                """INSERT INTO contacts (company_id, name, role, public_email, notes)
                VALUES (?, ?, ?, ?, ?)""",
                (company_id[0], ct["name"], ct["role"], ct.get("email"), ct.get("notes")),
            )

    conn.commit()
    conn.close()
    return db_path


def _get_companies():
    """Top 20 animal agriculture companies with publicly available data.
    Revenue figures sourced from Wikipedia, SEC filings, and annual reports.
    Data current as of early 2025 where available."""
    return [
        {
            "name": "JBS S.A.",
            "ticker": "JBSS3 / JBS",
            "industry": "Meat processing",
            "headquarters": "São Paulo, Brazil",
            "revenue": 77.2, "revenue_year": 2024,
            "employees": 270000,
            "animal_products": "beef, pork, chicken, lamb, salmon",
            "website": "https://jbs.com.br",
            "sustainability_claims": [
                "Net Zero by 2040 pledge",
                "Published sustainability report annually",
                "Claims to monitor deforestation in supply chain"
            ],
            "vulnerabilities": [
                {"category": "environmental", "severity": "critical", "description": "Linked to Amazon deforestation through cattle supply chain. Multiple investigations by Greenpeace and Global Witness."},
                {"category": "governance", "severity": "critical", "description": "Batista brothers (founders) convicted of bribery in 2017. J&F paid $3.2B fine — largest leniency deal in Brazilian history."},
                {"category": "labor", "severity": "high", "description": "Repeated allegations of labor violations in Brazilian and US facilities."},
                {"category": "regulatory", "severity": "high", "description": "Subject to antitrust investigations in multiple countries for alleged price-fixing in chicken and pork markets."},
                {"category": "greenwashing", "severity": "high", "description": "Net Zero 2040 pledge criticized as lacking credible pathway; emissions have increased since pledge."}
            ],
            "controversies": [
                "2017 bribery scandal — J&F $3.2B fine",
                "Linked to illegal Amazon deforestation (Greenpeace reports 2020-2024)",
                "Price-fixing lawsuits in US poultry market",
                "COVID-19 workplace safety failures",
                "Child labor allegations in supply chain"
            ],
            "notes": "World's largest meat processor. Dual-listed on B3 and NYSE as of 2025."
        },
        {
            "name": "Tyson Foods",
            "ticker": "TSN",
            "industry": "Meat processing",
            "headquarters": "Springdale, Arkansas, USA",
            "revenue": 54.4, "revenue_year": 2025,
            "employees": 133000,
            "animal_products": "beef, pork, chicken",
            "website": "https://tysonfoods.com",
            "sustainability_claims": [
                "Committed to 30% GHG reduction by 2030",
                "Published annual sustainability report",
                "Claims animal welfare improvements in supply chain"
            ],
            "vulnerabilities": [
                {"category": "labor", "severity": "critical", "description": "Under investigation for child labor violations. Multiple DOJ and DOL investigations 2022-2024."},
                {"category": "environmental", "severity": "high", "description": "Major water polluter. Facilities linked to nutrient runoff causing dead zones. EPA violations documented."},
                {"category": "animal_welfare", "severity": "high", "description": "Undercover investigations by Mercy For Animals, HSUS revealing animal abuse at facilities."},
                {"category": "antitrust", "severity": "high", "description": "Settled chicken price-fixing lawsuit. Part of broader industry antitrust scrutiny."},
                {"category": "worker_safety", "severity": "high", "description": "COVID-19 pandemic failures — managers allegedly bet on infection rates. Multiple wrongful death suits."}
            ],
            "controversies": [
                "Child labor investigation (2022-2024)",
                "Chicken price-fixing settlement",
                "COVID-19 manager betting scandal",
                "Wastewater pollution in multiple states",
                "Plant closures affecting rural communities (2023)",
                "Multiple undercover animal cruelty investigations"
            ],
            "notes": "Largest US meat company. Fortune 500 #85 (2025). Brands: Jimmy Dean, Hillshire Farm, Ball Park."
        },
        {
            "name": "Cargill",
            "ticker": None,
            "industry": "Agriculture / Meat processing",
            "headquarters": "Minnetonka, Minnesota, USA",
            "revenue": 165.0, "revenue_year": 2022,
            "employees": 160000,
            "animal_products": "beef, pork, chicken, turkey, eggs",
            "website": "https://cargill.com",
            "sustainability_claims": [
                "Pledged to eliminate deforestation from supply chain by 2030",
                "Climate targets across operations",
                "Sustainable cocoa and palm oil programs"
            ],
            "vulnerabilities": [
                {"category": "environmental", "severity": "critical", "description": "Linked to deforestation in South America and Southeast Asia. Major palm oil and soy trader. Dropped deforestation pledge timeline."},
                {"category": "transparency", "severity": "high", "description": "Privately held — minimal public financial disclosure. No SEC filings. Largest private US company."},
                {"category": "labor", "severity": "high", "description": "Child labor in cocoa supply chain documented by multiple NGOs."},
                {"category": "animal_welfare", "severity": "medium", "description": "Massive scale of animal processing with limited welfare commitments compared to peers."},
                {"category": "greenwashing", "severity": "high", "description": "Abandoned 2025 deforestation-free target. Mighty Earth and other NGOs have run sustained campaigns."}
            ],
            "controversies": [
                "Abandoned deforestation-free supply chain deadline",
                "Child labor in West African cocoa supply chain",
                "Major contributor to Amazon and Cerrado deforestation",
                "Lobbying against climate regulation",
                "Minimal transparency as largest private US company"
            ],
            "notes": "Largest privately held US company by revenue. Enormous scope across agriculture, meat, and commodities."
        },
        {
            "name": "Smithfield Foods",
            "ticker": "SFD",
            "industry": "Meat processing",
            "headquarters": "Smithfield, Virginia, USA",
            "revenue": 14.4, "revenue_year": 2015,
            "employees": 54000,
            "animal_products": "pork",
            "website": "https://smithfieldfoods.com",
            "sustainability_claims": [
                "Pledged 25% GHG reduction by 2025",
                "Manure-to-energy biogas projects",
                "Claims industry-leading animal care"
            ],
            "vulnerabilities": [
                {"category": "environmental", "severity": "critical", "description": "Massive hog waste lagoons in North Carolina causing air and water pollution. Disproportionately affects Black and low-income communities."},
                {"category": "environmental_justice", "severity": "critical", "description": "Environmental racism lawsuits — nuisance suits by neighbors won $473M (reduced on appeal). NAACP and Waterkeeper Alliance campaigns."},
                {"category": "ownership", "severity": "high", "description": "Owned by WH Group (China) since 2013 — $4.7B acquisition. National security concerns raised by lawmakers."},
                {"category": "labor", "severity": "high", "description": "COVID-19 outbreaks at plants, worker safety complaints."},
                {"category": "greenwashing", "severity": "medium", "description": "Biogas projects criticized as extending factory farm model rather than genuine sustainability."}
            ],
            "controversies": [
                "North Carolina hog waste pollution — environmental racism",
                "$473M nuisance lawsuit verdicts by plant neighbors",
                "WH Group (Chinese) ownership — national security debate",
                "COVID-19 plant outbreaks",
                "Antibiotic overuse concerns",
                "IPO in 2025 after years as WH Group subsidiary"
            ],
            "notes": "World's largest pork processor. Returned to public markets (Nasdaq: SFD) in 2025. Brands: Smithfield, Eckrich, Cook's."
        },
        {
            "name": "Hormel Foods",
            "ticker": "HRL",
            "industry": "Food processing",
            "headquarters": "Austin, Minnesota, USA",
            "revenue": 12.1, "revenue_year": 2024,
            "employees": 20000,
            "animal_products": "pork, chicken, turkey, beef",
            "website": "https://hormelfoods.com",
            "sustainability_claims": [
                "20 consecutive years in Civic 50 list",
                "Published responsibility report",
                "Animal welfare auditing program"
            ],
            "vulnerabilities": [
                {"category": "animal_welfare", "severity": "high", "description": "Jennie-O turkey brand subject to undercover investigations. Mercy For Animals investigation revealed animal abuse."},
                {"category": "labor", "severity": "medium", "description": "Historical labor disputes including famous 1985-86 Hormel strike in Austin, MN."},
                {"category": "product", "severity": "medium", "description": "SPAM and processed meat products face health scrutiny as WHO classifies processed meat as Group 1 carcinogen."}
            ],
            "controversies": [
                "Jennie-O Turkey undercover investigation (Mercy For Animals)",
                "Applegate brand accused of misleading 'natural' and 'humane' claims",
                "Processed meat health concerns (SPAM, etc.)"
            ],
            "notes": "S&P 500 company. Brands: SPAM, Jennie-O, Applegate, Hormel, Dinty Moore. Applegate is their 'natural/organic' brand."
        },
        {
            "name": "Perdue Farms",
            "ticker": None,
            "industry": "Poultry processing",
            "headquarters": "Salisbury, Maryland, USA",
            "revenue": 8.0, "revenue_year": 2021,
            "employees": 21000,
            "animal_products": "chicken, turkey, pork",
            "website": "https://perduefarms.com",
            "sustainability_claims": [
                "No antibiotics ever program",
                "Animal care commitments including third-party audits",
                "Organic and free-range product lines"
            ],
            "vulnerabilities": [
                {"category": "animal_welfare", "severity": "high", "description": "Despite welfare marketing, undercover investigations have documented crowded conditions. Compassion in World Farming campaigns."},
                {"category": "environmental", "severity": "medium", "description": "Poultry litter runoff on Delmarva Peninsula affecting Chesapeake Bay."},
                {"category": "greenwashing", "severity": "medium", "description": "Marketing emphasizes 'no antibiotics' and welfare but most birds still in conventional confinement."}
            ],
            "controversies": [
                "Chesapeake Bay pollution from poultry operations",
                "Misleading welfare marketing claims challenged by advocates",
                "Contract farmer exploitation concerns"
            ],
            "notes": "Privately held. Known for relatively progressive welfare marketing but criticized for gap between marketing and reality."
        },
        {
            "name": "Marfrig Global Foods",
            "ticker": "MRFG3",
            "industry": "Meat processing",
            "headquarters": "São Paulo, Brazil",
            "revenue": 13.0, "revenue_year": 2023,
            "employees": 30000,
            "animal_products": "beef, lamb",
            "website": "https://marfrig.com.br",
            "sustainability_claims": [
                "Marfrig Verde+ traceability program",
                "Committed to deforestation-free supply chain"
            ],
            "vulnerabilities": [
                {"category": "environmental", "severity": "critical", "description": "Linked to Amazon and Cerrado deforestation through cattle purchases. Amnesty International investigation."},
                {"category": "governance", "severity": "medium", "description": "Complex ownership structure. Significant stake in BRF S.A."}
            ],
            "controversies": [
                "Amazon deforestation linkage (Amnesty International)",
                "Indirect supplier monitoring gaps"
            ],
            "notes": "World's second-largest beef producer. Owns National Beef in the US."
        },
        {
            "name": "BRF S.A.",
            "ticker": "BRFS3",
            "industry": "Food processing",
            "headquarters": "São Paulo, Brazil",
            "revenue": 14.0, "revenue_year": 2023,
            "employees": 90000,
            "animal_products": "chicken, pork",
            "website": "https://bfrsa.com",
            "sustainability_claims": [
                "Sustainability-linked bond issuance",
                "GHG reduction targets"
            ],
            "vulnerabilities": [
                {"category": "food_safety", "severity": "critical", "description": "Operation Weak Flesh (2017) — Brazilian federal police found BRF bribing inspectors to approve rotten meat."},
                {"category": "governance", "severity": "high", "description": "Multiple executive turnover, regulatory investigations."}
            ],
            "controversies": [
                "Operation Weak Flesh meat safety scandal (2017)",
                "Bribery of food safety inspectors",
                "Export bans from multiple countries after scandal"
            ],
            "notes": "One of world's largest poultry exporters. Brands: Sadia, Perdigão."
        },
        {
            "name": "Pilgrim's Pride",
            "ticker": "PPC",
            "industry": "Poultry processing",
            "headquarters": "Greeley, Colorado, USA",
            "revenue": 17.5, "revenue_year": 2023,
            "employees": 60000,
            "animal_products": "chicken, pork",
            "website": "https://pilgrims.com",
            "sustainability_claims": [
                "Published sustainability report",
                "Better Chicken Commitment partial adoption"
            ],
            "vulnerabilities": [
                {"category": "antitrust", "severity": "critical", "description": "Former CEO Jayson Penn indicted for chicken price-fixing conspiracy. Company paid $110M penalty."},
                {"category": "labor", "severity": "high", "description": "Worker safety violations, COVID-19 outbreaks."},
                {"category": "animal_welfare", "severity": "high", "description": "Undercover investigations documenting animal cruelty at facilities."}
            ],
            "controversies": [
                "CEO indicted for price-fixing (2020)",
                "$110M antitrust penalty",
                "COVID-19 plant outbreaks",
                "Animal cruelty investigations"
            ],
            "notes": "Majority owned by JBS (80%+). Second-largest US chicken producer."
        },
        {
            "name": "Sanderson Farms",
            "ticker": "SAFM (delisted)",
            "industry": "Poultry processing",
            "headquarters": "Laurel, Mississippi, USA",
            "revenue": 7.0, "revenue_year": 2022,
            "employees": 17000,
            "animal_products": "chicken",
            "website": "https://sandersonfarms.com",
            "sustainability_claims": [
                "No antibiotics important to human medicine"
            ],
            "vulnerabilities": [
                {"category": "antitrust", "severity": "high", "description": "Named in poultry price-fixing litigation."},
                {"category": "environmental", "severity": "medium", "description": "Water pollution from processing plants in Mississippi."}
            ],
            "controversies": [
                "Poultry price-fixing litigation",
                "Merged with Wayne Farms under Cargill ownership (2022)"
            ],
            "notes": "Acquired by Cargill and Continental Grain in 2022. Now part of Wayne-Sanderson Farms."
        },
        {
            "name": "Maple Leaf Foods",
            "ticker": "MFI.TO",
            "industry": "Meat processing",
            "headquarters": "Mississauga, Ontario, Canada",
            "revenue": 3.5, "revenue_year": 2023,
            "employees": 14000,
            "animal_products": "pork, chicken",
            "website": "https://mapleleaffoods.com",
            "sustainability_claims": [
                "Claims to be world's first major carbon-neutral food company (2019)",
                "Animal Care commitment with third-party audits",
                "Published detailed sustainability report"
            ],
            "vulnerabilities": [
                {"category": "greenwashing", "severity": "medium", "description": "Carbon neutrality claim relies heavily on offsets rather than absolute emissions reductions."},
                {"category": "food_safety", "severity": "medium", "description": "2008 listeriosis outbreak killed 22 people — Canada's worst food safety disaster."}
            ],
            "controversies": [
                "2008 listeriosis outbreak (22 deaths)",
                "Carbon neutrality claim criticized as offset-dependent",
                "Spun off plant-based division (Greenleaf Foods) due to poor performance"
            ],
            "notes": "Interesting case study — most progressive major meat company on sustainability, but still faces criticism."
        },
        {
            "name": "National Beef Packing",
            "ticker": None,
            "industry": "Beef processing",
            "headquarters": "Kansas City, Missouri, USA",
            "revenue": 11.0, "revenue_year": 2023,
            "employees": 10000,
            "animal_products": "beef",
            "website": "https://nationalbeef.com",
            "sustainability_claims": [],
            "vulnerabilities": [
                {"category": "transparency", "severity": "high", "description": "Privately held by Marfrig. Limited public disclosure."},
                {"category": "labor", "severity": "medium", "description": "Worker safety concerns in meatpacking."},
                {"category": "antitrust", "severity": "medium", "description": "Part of Big 4 beef packers controlling ~85% of US market."}
            ],
            "controversies": [
                "Part of oligopolistic beef packing market",
                "Worker safety violations"
            ],
            "notes": "Fourth-largest US beef packer. Owned by Marfrig (Brazil)."
        },
        {
            "name": "Minerva Foods",
            "ticker": "BEEF3",
            "industry": "Beef processing",
            "headquarters": "Barretos, São Paulo, Brazil",
            "revenue": 7.5, "revenue_year": 2023,
            "employees": 20000,
            "animal_products": "beef, lamb",
            "website": "https://minervafoods.com",
            "sustainability_claims": [
                "Cattle traceability program",
                "Deforestation monitoring via satellite"
            ],
            "vulnerabilities": [
                {"category": "environmental", "severity": "high", "description": "South American cattle supply chain linked to deforestation despite monitoring programs."},
                {"category": "market_concentration", "severity": "medium", "description": "Acquiring Marfrig assets, increasing market concentration in South American beef."}
            ],
            "controversies": [
                "Deforestation linkage in cattle supply chain",
                "Antitrust review of Marfrig asset acquisition"
            ],
            "notes": "Largest beef exporter in South America."
        },
        {
            "name": "Danish Crown",
            "ticker": None,
            "industry": "Meat processing",
            "headquarters": "Randers, Denmark",
            "revenue": 11.0, "revenue_year": 2023,
            "employees": 26000,
            "animal_products": "pork, beef",
            "website": "https://danishcrown.com",
            "sustainability_claims": [
                "Climate target: carbon neutral by 2050",
                "Welfare controlled supply chain",
                "Invested in plant-based alternatives"
            ],
            "vulnerabilities": [
                {"category": "animal_welfare", "severity": "high", "description": "Undercover investigations in Danish pig farms revealing confinement conditions (Animal Equality)."},
                {"category": "environmental", "severity": "medium", "description": "Denmark's pig industry major nitrogen polluter affecting waterways."}
            ],
            "controversies": [
                "Danish pig farming welfare investigations",
                "Nitrogen pollution from intensive pig farming"
            ],
            "notes": "Cooperative owned by Danish farmers. Europe's largest pork producer."
        },
        {
            "name": "Vion Food Group",
            "ticker": None,
            "industry": "Meat processing",
            "headquarters": "Eindhoven, Netherlands",
            "revenue": 5.5, "revenue_year": 2023,
            "employees": 12000,
            "animal_products": "pork, beef",
            "website": "https://vionfoodgroup.com",
            "sustainability_claims": [
                "Good Farming Star sustainability program",
                "Better Life quality mark participation"
            ],
            "vulnerabilities": [
                {"category": "labor", "severity": "high", "description": "Dutch meat industry labor exploitation of migrant workers. Parliamentary investigations."},
                {"category": "food_safety", "severity": "medium", "description": "Processing plant hygiene violations documented."}
            ],
            "controversies": [
                "Migrant worker exploitation in Dutch meat plants",
                "Processing plant hygiene issues"
            ],
            "notes": "Major European pork and beef processor."
        },
        {
            "name": "WH Group",
            "ticker": "0288.HK",
            "industry": "Meat processing",
            "headquarters": "Hong Kong / Luohe, China",
            "revenue": 24.0, "revenue_year": 2023,
            "employees": 100000,
            "animal_products": "pork",
            "website": "https://whgroup.com",
            "sustainability_claims": [
                "Published ESG report",
                "Food safety management systems"
            ],
            "vulnerabilities": [
                {"category": "governance", "severity": "high", "description": "Complex cross-border ownership structure. Owns Smithfield Foods (US). Geopolitical risk."},
                {"category": "food_safety", "severity": "high", "description": "Chinese operations have faced food safety scandals historically."},
                {"category": "animal_welfare", "severity": "high", "description": "Minimal animal welfare standards in Chinese operations."}
            ],
            "controversies": [
                "Geopolitical concerns over Chinese ownership of US food supply",
                "Historical food safety issues in China",
                "Smithfield Foods subsidiary controversies"
            ],
            "notes": "Parent of Smithfield Foods. World's largest pork company by volume."
        },
        {
            "name": "Koch Foods",
            "ticker": None,
            "industry": "Poultry processing",
            "headquarters": "Park Ridge, Illinois, USA",
            "revenue": 4.0, "revenue_year": 2023,
            "employees": 14000,
            "animal_products": "chicken",
            "website": "https://kochfoods.com",
            "sustainability_claims": [],
            "vulnerabilities": [
                {"category": "labor", "severity": "critical", "description": "2019 ICE raids at Mississippi plants — 680 workers detained. Largest single-state workplace raid in US history."},
                {"category": "antitrust", "severity": "high", "description": "Named in chicken price-fixing conspiracy."},
                {"category": "labor", "severity": "high", "description": "Sexual harassment and hostile work environment lawsuits by workers."}
            ],
            "controversies": [
                "2019 ICE raids — 680 workers detained",
                "Chicken price-fixing conspiracy",
                "Sexual harassment lawsuits",
                "Worker exploitation allegations"
            ],
            "notes": "Not related to Koch Industries. Major US chicken processor."
        },
        {
            "name": "Mountaire Farms",
            "ticker": None,
            "industry": "Poultry processing",
            "headquarters": "Millsboro, Delaware, USA",
            "revenue": 4.0, "revenue_year": 2023,
            "employees": 10000,
            "animal_products": "chicken",
            "website": "https://mountaire.com",
            "sustainability_claims": [],
            "vulnerabilities": [
                {"category": "environmental", "severity": "critical", "description": "Major pollution violations in Delaware. $600K+ EPA fine. Wastewater discharge polluting Indian River and surrounding communities."},
                {"category": "labor", "severity": "medium", "description": "Worker safety complaints at processing facilities."}
            ],
            "controversies": [
                "EPA fines for wastewater violations",
                "Indian River pollution affecting Delaware communities",
                "DNREC enforcement actions"
            ],
            "notes": "Privately held. Fourth-largest US chicken company. Known for Delaware pollution issues."
        },
        {
            "name": "Cal-Maine Foods",
            "ticker": "CALM",
            "industry": "Egg production",
            "headquarters": "Ridgeland, Mississippi, USA",
            "revenue": 3.1, "revenue_year": 2024,
            "employees": 3500,
            "animal_products": "eggs",
            "website": "https://calmainefoods.com",
            "sustainability_claims": [
                "Transitioning to cage-free housing",
                "Published animal welfare policy"
            ],
            "vulnerabilities": [
                {"category": "animal_welfare", "severity": "critical", "description": "Largest US egg producer. HSUS and other groups have run sustained campaigns for cage-free transition. Undercover investigations at facilities."},
                {"category": "antitrust", "severity": "high", "description": "Accused of price gouging during egg shortage/avian flu crises."},
                {"category": "animal_welfare", "severity": "high", "description": "Avian flu response involves mass culling — millions of birds killed."}
            ],
            "controversies": [
                "Egg price gouging allegations during avian flu",
                "Cage-free transition pace criticized as too slow",
                "Undercover investigations at egg facilities",
                "Mass culling during avian flu outbreaks"
            ],
            "notes": "Largest US shell egg producer. Publicly traded. Key target for cage-free campaigns."
        },
        {
            "name": "Dairy Farmers of America",
            "ticker": None,
            "industry": "Dairy",
            "headquarters": "Kansas City, Kansas, USA",
            "revenue": 21.0, "revenue_year": 2023,
            "employees": 8000,
            "animal_products": "dairy",
            "website": "https://dfamilk.com",
            "sustainability_claims": [
                "Sustainability commitment for member farms",
                "GHG reduction initiatives"
            ],
            "vulnerabilities": [
                {"category": "antitrust", "severity": "high", "description": "Antitrust lawsuits alleging market manipulation that depressed prices paid to non-member dairy farmers."},
                {"category": "animal_welfare", "severity": "medium", "description": "Dairy industry practices — calf separation, continuous pregnancy cycles — face growing public scrutiny."},
                {"category": "environmental", "severity": "medium", "description": "Dairy methane emissions. Large-scale operations contribute significantly to agricultural GHG."}
            ],
            "controversies": [
                "Antitrust litigation over milk pricing",
                "Dean Foods bankruptcy connection",
                "Growing public awareness of dairy welfare issues"
            ],
            "notes": "Cooperative. Largest US dairy cooperative. Markets milk from ~12,000 member farms."
        },
    ]


def _get_campaigns():
    """Known advocacy campaigns against these companies from public sources."""
    return [
        {"company": "JBS S.A.", "type": "environmental", "name": "JBS: Linked to Amazon Destruction",
         "organizer": "Greenpeace", "status": "active", "start_year": 2009,
         "description": "Ongoing Greenpeace campaign documenting JBS links to illegal Amazon deforestation through cattle supply chain."},
        {"company": "JBS S.A.", "type": "investor_pressure", "name": "FAIRR Climate Risk Engagement",
         "organizer": "FAIRR Initiative", "status": "active", "start_year": 2018,
         "description": "Investor coalition engaging JBS on climate risk, deforestation, and protein diversification."},
        {"company": "Tyson Foods", "type": "shareholder_resolution", "name": "Tyson Deforestation Resolution",
         "organizer": "Green Century Funds", "status": "completed", "start_year": 2021,
         "outcome": "Resolution received 25%+ support, company made new commitments"},
        {"company": "Tyson Foods", "type": "consumer", "name": "Tyson Torture Investigation",
         "organizer": "Mercy For Animals", "status": "completed", "start_year": 2015,
         "description": "Undercover investigation revealing animal abuse at Tyson chicken supplier farms."},
        {"company": "Cargill", "type": "environmental", "name": "Cargill: The Worst Company in the World",
         "organizer": "Mighty Earth", "status": "active", "start_year": 2019,
         "description": "Mighty Earth campaign naming Cargill worst company for environmental destruction, focusing on deforestation and ecosystem destruction."},
        {"company": "Smithfield Foods", "type": "legal", "name": "Smithfield Nuisance Lawsuits",
         "organizer": "Community plaintiffs", "status": "completed", "start_year": 2014,
         "outcome": "$473M in jury verdicts (reduced to ~$98M on appeal). Set precedent for community claims against factory farms."},
        {"company": "Smithfield Foods", "type": "environmental", "name": "Smithfield North Carolina Pollution Campaign",
         "organizer": "Waterkeeper Alliance / NAACP", "status": "active", "start_year": 2014,
         "description": "Ongoing campaign against hog waste pollution in North Carolina disproportionately affecting communities of color."},
        {"company": "Hormel Foods", "type": "consumer", "name": "Jennie-O Turkey Investigation",
         "organizer": "Mercy For Animals", "status": "completed", "start_year": 2017,
         "description": "Undercover investigation at Jennie-O turkey facilities documenting abuse."},
        {"company": "Perdue Farms", "type": "consumer", "name": "Better Chicken Campaign",
         "organizer": "The Humane League", "status": "completed", "start_year": 2017,
         "outcome": "Perdue made commitments to improve chicken welfare standards, though implementation is slow."},
        {"company": "Pilgrim's Pride", "type": "legal", "name": "Chicken Price-Fixing Criminal Case",
         "organizer": "US DOJ", "status": "completed", "start_year": 2020,
         "outcome": "CEO Jayson Penn indicted. Company paid $110M. Multiple executives convicted."},
        {"company": "Cal-Maine Foods", "type": "consumer", "name": "Cage-Free Campaign",
         "organizer": "HSUS / Mercy For Animals", "status": "active", "start_year": 2015,
         "description": "Sustained campaign pressuring Cal-Maine and the egg industry to transition to cage-free housing."},
        {"company": "Koch Foods", "type": "labor", "name": "Mississippi ICE Raids Response",
         "organizer": "SPLC / worker advocates", "status": "completed", "start_year": 2019,
         "description": "Advocacy response to largest single-state ICE workplace raid. 680 workers detained at Koch Foods and other plants."},
        {"company": "Danish Crown", "type": "consumer", "name": "Danish Pig Farming Investigation",
         "organizer": "Animal Equality", "status": "completed", "start_year": 2019,
         "description": "Undercover investigation in Danish pig farms supplying Danish Crown, revealing confinement conditions."},
        {"company": "Dairy Farmers of America", "type": "legal", "name": "Dairy Antitrust Litigation",
         "organizer": "Independent dairy farmers", "status": "active", "start_year": 2009,
         "description": "Class-action alleging DFA conspired to monopolize milk market and depress prices."},
        {"company": "Mountaire Farms", "type": "regulatory", "name": "EPA Enforcement Action",
         "organizer": "EPA / DNREC", "status": "completed", "start_year": 2018,
         "outcome": "Fines and consent decree for wastewater violations polluting Delaware waterways."},
        {"company": "Maple Leaf Foods", "type": "consumer", "name": "Carbon Neutral Scrutiny",
         "organizer": "Various environmental groups", "status": "active", "start_year": 2020,
         "description": "Scrutiny of Maple Leaf's carbon neutrality claim as overly reliant on offsets rather than real reductions."},
        {"company": "WH Group", "type": "regulatory", "name": "CFIUS National Security Review",
         "organizer": "US lawmakers", "status": "completed", "start_year": 2013,
         "outcome": "Acquisition of Smithfield approved but ongoing concern about Chinese ownership of US food infrastructure."},
        {"company": "Marfrig Global Foods", "type": "environmental", "name": "Marfrig Amazon Deforestation Report",
         "organizer": "Amnesty International", "status": "completed", "start_year": 2020,
         "description": "Investigation linking Marfrig cattle purchases to illegally deforested Amazon land."},
    ]


def _get_contacts():
    """Key decision-makers — publicly available names and roles only."""
    return [
        {"company": "JBS S.A.", "name": "Gilberto Tomazoni", "role": "Global CEO"},
        {"company": "JBS S.A.", "name": "Wesley Batista", "role": "Co-owner (J&F Investimentos)"},
        {"company": "Tyson Foods", "name": "Donnie King", "role": "CEO"},
        {"company": "Tyson Foods", "name": "John H. Tyson", "role": "Chairman"},
        {"company": "Cargill", "name": "Brian Sikes", "role": "Chairman & CEO"},
        {"company": "Smithfield Foods", "name": "Shane Smith", "role": "CEO"},
        {"company": "Hormel Foods", "name": "Jim Snee", "role": "CEO", "notes": "Jeff Ettinger served as interim CEO previously"},
        {"company": "Perdue Farms", "name": "Jim Perdue", "role": "Chairman"},
        {"company": "Perdue Farms", "name": "Kevin McAdams", "role": "CEO"},
        {"company": "Pilgrim's Pride", "name": "Fabio Sandri", "role": "CEO"},
        {"company": "Cal-Maine Foods", "name": "Sherman Miller", "role": "CEO"},
        {"company": "Danish Crown", "name": "Jais Valeur", "role": "Group CEO"},
        {"company": "WH Group", "name": "Wan Long", "role": "Chairman"},
        {"company": "Maple Leaf Foods", "name": "Curtis Frank", "role": "CEO"},
        {"company": "BRF S.A.", "name": "Miguel Gularte", "role": "CEO"},
        {"company": "Marfrig Global Foods", "name": "Marcos Molina", "role": "Chairman & Founder"},
        {"company": "Dairy Farmers of America", "name": "Dennis Rodenbaugh", "role": "CEO"},
    ]


if __name__ == "__main__":
    path = init_db()
    print(f"Database initialized at {path}")
