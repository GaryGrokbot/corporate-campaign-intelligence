from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Corporate Campaign Intelligence API")

class Vulnerability(BaseModel):
    category: str
    severity: str
    description: str
    evidence: List[str]

class CampaignStrategy(BaseModel):
    company_name: str
    goal: str
    vulnerabilities: List[Vulnerability]
    recommended_tactics: List[str]
    target_decision_makers: List[str]
    timeline_months: int
    estimated_budget_usd: int
    success_probability: float

@app.get("/")
async def root():
    return {"status": "Corporate Campaign Intelligence API", "version": "0.1.0"}

@app.post("/api/analyze/{company_name}", response_model=CampaignStrategy)
async def analyze_company(company_name: str, goal: Optional[str] = "Animal welfare improvement"):
    return CampaignStrategy(
        company_name=company_name,
        goal=goal,
        vulnerabilities=[
            Vulnerability(
                category="regulatory",
                severity="high",
                description="EPA violations pattern",
                evidence=["3 violations in 12 months"]
            )
        ],
        recommended_tactics=["Investor pressure", "Regulatory complaints", "Customer leverage"],
        target_decision_makers=["CEO", "ESG Committee", "Major investors"],
        timeline_months=12,
        estimated_budget_usd=100000,
        success_probability=0.6
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
