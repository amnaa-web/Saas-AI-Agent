from __future__ import annotations
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="ProMatch B2B SaaS MVP", version="1.0.0")

CANDIDATES = [
    {
        "id":"cand-001",
        "name":"Anna Lindberg",
        "title":"Registered Nurse",
        "category":"Healthcare",
        "location":"Stockholm",
        "availability":"Available now",
        "skills":["elder care","patient documentation","medication handling"],
        "years_experience":8,
        "qualifications":["Registered Nurse","BSc Nursing"],
        "verification_level":"independently_confirmed",
        "verified_documents":4,
        "total_documents":4,
        "profile_visibility":"approved_employers",
        "passport_token":"PASS-ANNA-001"
    },
    {
        "id":"cand-002",
        "name":"Erik Svensson",
        "title":"Industrial Electrician",
        "category":"Engineering",
        "location":"Gothenburg",
        "availability":"2 weeks",
        "skills":["industrial maintenance","PLC","electrical safety"],
        "years_experience":6,
        "qualifications":["Electrician Certificate"],
        "verification_level":"document_checked",
        "verified_documents":2,
        "total_documents":3,
        "profile_visibility":"approved_employers",
        "passport_token":"PASS-ERIK-002"
    },
    {
        "id":"cand-003",
        "name":"Sara Holm",
        "title":"Care Assistant",
        "category":"Healthcare",
        "location":"Stockholm",
        "availability":"Available now",
        "skills":["elder care","home care","Swedish B2"],
        "years_experience":4,
        "qualifications":["Care Assistant Diploma"],
        "verification_level":"self_reported",
        "verified_documents":1,
        "total_documents":2,
        "profile_visibility":"approved_employers",
        "passport_token":"PASS-SARA-003"
    },
    {
        "id":"cand-004",
        "name":"Ahmed Khan",
        "title":"Software Engineer",
        "category":"Technology",
        "location":"Stockholm",
        "availability":"Available now",
        "skills":["Python","Node.js","PostgreSQL","REST APIs","Docker"],
        "years_experience":7,
        "qualifications":["BSc Computer Science","AWS Cloud Practitioner"],
        "verification_level":"independently_confirmed",
        "verified_documents":5,
        "total_documents":5,
        "profile_visibility":"approved_employers",
        "passport_token":"PASS-AHMED-004"
    },
    {
        "id":"cand-005",
        "name":"Linnea Berg",
        "title":"Frontend Developer",
        "category":"Technology",
        "location":"Stockholm",
        "availability":"1 week",
        "skills":["React","Next.js","TypeScript","CSS","Accessibility"],
        "years_experience":5,
        "qualifications":["BSc Software Engineering"],
        "verification_level":"document_checked",
        "verified_documents":3,
        "total_documents":4,
        "profile_visibility":"approved_employers",
        "passport_token":"PASS-LINNEA-005"
    },
    {
        "id":"cand-006",
        "name":"Omar Ali",
        "title":"AI Engineer",
        "category":"Technology",
        "location":"Malmo",
        "availability":"Available now",
        "skills":["Python","LLMs","RAG","FastAPI","Vector Databases"],
        "years_experience":6,
        "qualifications":["MSc Artificial Intelligence"],
        "verification_level":"independently_confirmed",
        "verified_documents":4,
        "total_documents":4,
        "profile_visibility":"approved_employers",
        "passport_token":"PASS-OMAR-006"
    },
    {
        "id":"cand-007",
        "name":"Elsa Nordin",
        "title":"Data Engineer",
        "category":"Technology",
        "location":"Gothenburg",
        "availability":"3 weeks",
        "skills":["Python","SQL","PostgreSQL","ETL","AWS"],
        "years_experience":6,
        "qualifications":["MSc Data Engineering"],
        "verification_level":"document_checked",
        "verified_documents":3,
        "total_documents":3,
        "profile_visibility":"approved_employers",
        "passport_token":"PASS-ELSA-007"
    }
]

VERIFICATION_QUEUE = [
    {"id":"ver-101","candidate_id":"cand-002","candidate_name":"Erik Svensson","document":"Electrical Safety Certificate","status":"needs_review","expires_on":"2027-04-30"},
    {"id":"ver-102","candidate_id":"cand-003","candidate_name":"Sara Holm","document":"Employment Reference","status":"additional_info_requested","expires_on":None}
]

CONTRACTS = [
    {"id":"ctr-001","company":"Nordic Care AB","template":"Business Subscription Agreement","status":"sent","provider":"Oneflow / Scrive ready","updated_at":"2026-10-20T10:00:00Z"}
]
AUDIT_LOG=[]

def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

class MatchRequest(BaseModel):
    role_title: str = Field(min_length=2,max_length=120)
    location: str|None = None
    mandatory_skill: str|None = None
    min_experience: int = Field(default=0,ge=0,le=50)
    required_verification: Literal["any","document_checked","independently_confirmed"]="any"
    strict_role_match: bool = True

class VerifyRequest(BaseModel):
    status: Literal["approved","rejected","additional_info_requested"]

class ContractRequest(BaseModel):
    company: str = Field(min_length=2,max_length=120)
    template: str = Field(min_length=2,max_length=200)

@app.get("/")
def home(): return FileResponse(BASE_DIR/"index.html")

@app.get("/styles.css")
def styles(): return FileResponse(BASE_DIR/"styles.css",media_type="text/css")

@app.get("/app.js")
def javascript(): return FileResponse(BASE_DIR/"app.js",media_type="application/javascript")

@app.get("/api/health")
def health():
    return {"status":"ok","mode":"safe-demo","tenant_isolation":"demo","ai_provider":"provider-agnostic demo","stripe":"demo","esign":"demo"}

@app.get("/api/candidates")
def candidates(): return CANDIDATES

@app.post("/api/match")
def match(req:MatchRequest):
    level_score={"self_reported":1,"document_checked":2,"independently_confirmed":3}
    required_level={"any":0,"document_checked":2,"independently_confirmed":3}[req.required_verification]
    results=[]

    role_query=req.role_title.strip().lower()

    for c in CANDIDATES:
        fulfilled=[]
        missing=[]
        hard_fail=False

        # Role title is a true eligibility criterion in strict mode.
        role_match = role_query in c["title"].lower() or c["title"].lower() in role_query
        if role_match:
            fulfilled.append(f"Role: {c['title']}")
        elif req.strict_role_match:
            missing.append(f"Role mismatch: {c['title']}")
            hard_fail=True

        if req.location:
            if c["location"].lower()==req.location.lower():
                fulfilled.append(f"Location: {c['location']}")
            else:
                missing.append(f"Location mismatch: {c['location']}")
                hard_fail=True

        if c["years_experience"]>=req.min_experience:
            fulfilled.append(f"Experience: {c['years_experience']} years")
        else:
            missing.append(f"Needs {req.min_experience}+ years")
            hard_fail=True

        if req.mandatory_skill:
            has_skill=any(req.mandatory_skill.lower() in s.lower() for s in c["skills"])
            if has_skill:
                fulfilled.append(f"Skill: {req.mandatory_skill}")
            else:
                missing.append(f"Missing skill: {req.mandatory_skill}")
                hard_fail=True

        if level_score[c["verification_level"]]>=required_level:
            fulfilled.append(f"Verification: {c['verification_level']}")
        else:
            missing.append("Verification below required level")
            hard_fail=True

        if hard_fail:
            continue

        # Ranking only happens after all mandatory checks pass.
        score=55
        score += min(c["years_experience"]*3,20)
        score += level_score[c["verification_level"]]*5
        if role_match:
            score += 10
        if req.mandatory_skill and any(req.mandatory_skill.lower() in s.lower() for s in c["skills"]):
            score += 5
        score=min(score,100)

        results.append({
            "candidate":c,
            "score":score,
            "fulfilled":fulfilled,
            "missing":missing,
            "verified_evidence":{
                "qualifications":c["qualifications"],
                "documents_verified":f"{c['verified_documents']}/{c['total_documents']}",
                "verification_level":c["verification_level"]
            },
            "explanation":"Candidate passed all mandatory rules before ranking. The system does not invent qualifications, certifications, location, experience, or verification status."
        })

    results.sort(key=lambda x:x["score"],reverse=True)

    AUDIT_LOG.append({
        "event":"candidate_match",
        "criteria":req.model_dump(),
        "results":len(results),
        "at":utc_now()
    })

    return {
        "criteria":req.model_dump(),
        "matches":results,
        "fallback":"rule-based search remains available if AI provider is unavailable",
        "protected_attributes_used":False,
        "hallucination_guard":"Only stored candidate fields and verified evidence are used."
    }

@app.get("/api/verification")
def verification(): return VERIFICATION_QUEUE

@app.post("/api/verification/{verification_id}")
def update_verification(verification_id:str,req:VerifyRequest):
    for item in VERIFICATION_QUEUE:
        if item["id"]==verification_id:
            item["status"]=req.status
            AUDIT_LOG.append({"event":"verification_status_changed","verification_id":verification_id,"status":req.status,"at":utc_now()})
            return item
    raise HTTPException(404,"Verification record not found")

@app.get("/api/contracts")
def contracts(): return CONTRACTS

@app.post("/api/contracts")
def create_contract(req:ContractRequest):
    contract={"id":f"ctr-{str(uuid.uuid4())[:6]}","company":req.company,"template":req.template,"status":"draft","provider":"Oneflow / Scrive ready","updated_at":utc_now()}
    CONTRACTS.append(contract)
    AUDIT_LOG.append({"event":"contract_created","contract_id":contract["id"],"at":utc_now()})
    return contract

@app.get("/api/subscription")
def subscription():
    return {"company":"Nordic Care AB","plan":"Growth","billing":"monthly","company_users":{"used":7,"limit":10},"candidate_contacts":{"used":42,"limit":100},"status":"active","provider":"Stripe-ready demo"}

@app.get("/api/costs")
def costs():
    return {"pilot_100_500":{"aws_eu_hosting_db_storage":"$100–$250/mo","ai_matching":"$30–$150/mo","email_sms":"$20–$80/mo","monitoring_backups_security":"$30–$100/mo","esignature":"$50–$200+/mo","stripe":"transaction-based","estimated_total_excluding_maintenance":"$230–$780+/mo"},"note":"Illustrative MVP estimate only; final vendor quotes depend on actual usage, SLA and provider contracts."}

@app.get("/api/audit")
def audit(): return list(reversed(AUDIT_LOG[-50:]))
