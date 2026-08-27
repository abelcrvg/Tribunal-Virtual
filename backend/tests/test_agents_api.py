from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def test_agents_route_requires_process():
    response=client.get('/api/v1/processes/00000000-0000-0000-0000-000000000000/agents')
    assert response.status_code==404

def test_agent_registry_is_exposed_after_process_creation():
    payload={'area':'consumer','plaintiff':'João da Silva','defendant':'Empresa Fictícia Ltda','facts':'O consumidor adquiriu um produto que apresentou defeito após a entrega.','include_mp':False,'jury':False}
    created=client.post('/api/v1/processes',json=payload)
    assert created.status_code in (200,201)
    pid=created.json()['id']
    response=client.get(f'/api/v1/processes/{pid}/agents')
    assert response.status_code==200
    roles={item['role'] for item in response.json()['agents']}
    assert {'judge','plaintiff_attorney','defense_attorney'} <= roles
