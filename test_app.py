from fastapi.testclient import TestClient
from server import app

client=TestClient(app)

def test_health():
    r=client.get("/api/health")
    assert r.status_code==200
    assert r.json()["status"]=="ok"

def test_match_filters_mandatory_requirements():
    r=client.post("/api/match",json={
        "role_title":"Registered Nurse",
        "location":"Stockholm",
        "mandatory_skill":"elder care",
        "min_experience":5,
        "required_verification":"independently_confirmed"
    })
    assert r.status_code==200
    d=r.json()
    assert len(d["matches"])==1
    assert d["matches"][0]["candidate"]["id"]=="cand-001"
    assert d["protected_attributes_used"] is False

def test_verification_update():
    r=client.post("/api/verification/ver-101",json={"status":"approved"})
    assert r.status_code==200
    assert r.json()["status"]=="approved"

def test_contract_creation():
    r=client.post("/api/contracts",json={
        "company":"Demo Employer AB",
        "template":"Business Subscription Agreement"
    })
    assert r.status_code==200
    assert r.json()["status"]=="draft"

def test_subscription():
    r=client.get("/api/subscription")
    assert r.status_code==200
    assert r.json()["status"]=="active"

def test_verified_software_engineer_match():
    r=client.post("/api/match",json={
        "role_title":"Software Engineer",
        "location":"Stockholm",
        "mandatory_skill":"Python",
        "min_experience":5,
        "required_verification":"independently_confirmed",
        "strict_role_match":True
    })
    assert r.status_code==200
    d=r.json()
    assert len(d["matches"])==1
    assert d["matches"][0]["candidate"]["id"]=="cand-004"
    assert d["matches"][0]["candidate"]["verification_level"]=="independently_confirmed"

def test_strict_role_prevents_wrong_job_match():
    r=client.post("/api/match",json={
        "role_title":"Software Engineer",
        "location":"Stockholm",
        "mandatory_skill":"elder care",
        "min_experience":1,
        "required_verification":"any",
        "strict_role_match":True
    })
    assert r.status_code==200
    assert r.json()["matches"]==[]
