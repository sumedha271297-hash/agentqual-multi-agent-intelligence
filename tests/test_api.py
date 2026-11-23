from fastapi.testclient import TestClient
from app.api import app
client=TestClient(app)
ICP={'industries':['SaaS','Fintech'],'min_employees':20,'max_employees':300,'regions':['US']}

def test_health():
    assert client.get('/health').status_code==200

def test_run():
    r=client.post('/offline/run',json={'company_id':'c01','icp':ICP})
    assert r.status_code==200 and r.json()['sent'] is False

def test_invalid_company():
    assert client.post('/offline/run',json={'company_id':'bad','icp':ICP}).status_code==404
