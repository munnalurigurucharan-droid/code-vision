import io
import zipfile
from app.main import app, memory


def test_health(client):
    r=client.get('/api/health')
    assert r.status_code==200
    assert r.json()['hindsight_verified'] is False


def test_demo_load_and_explain(client):
    r=client.post('/api/demo')
    assert r.status_code==200
    project=r.json()
    assert project['stats']['files'] >= 5
    r=client.post(f"/api/projects/{project['id']}/ask",json={'question':'Why is token validation failing?','use_memory':False})
    assert r.status_code==200
    assert r.json()['provider']=='static-only'
    assert r.json()['memory_status']=='disabled'
    assert 'src/auth.py' in [x['path'] for x in project['files']]


def test_unconfigured_memory_never_claims_success(client):
    project=client.post('/api/demo').json()
    r=client.post(f"/api/projects/{project['id']}/demo/remember")
    assert r.status_code==503
    assert client.get(f"/api/projects/{project['id']}/resolutions").json()==[]
    r=client.post(f"/api/projects/{project['id']}/ask",json={'question':'Is the token suffix bug back?'})
    assert r.json()['memory_status']=='not-configured'
    assert r.json()['memories']==[]


def test_memory_api_with_real_adapter_contract_mock(client, monkeypatch):
    project=client.post('/api/demo').json(); pid=project['id']
    calls=[]
    async def fake_retain(project_id,content):
        calls.append((project_id,content))
    async def fake_recall(project_id,query):
        return [{'id':'mem-123','text':'Previously fixed src/auth.py startswith issue'}]
    async def fake_reflect(project_id,query):
        return 'The prior fix was strict comparison.'
    monkeypatch.setattr(memory,'retain',fake_retain)
    monkeypatch.setattr(memory,'recall',fake_recall)
    monkeypatch.setattr(memory,'reflect',fake_reflect)
    monkeypatch.setattr(type(memory),'configured',property(lambda self: True))
    r=client.post(f'/api/projects/{pid}/demo/remember')
    assert r.status_code==200 and r.json()['stored_in_hindsight']
    assert 'startsWith' not in calls[0][1]
    q=client.post(f'/api/projects/{pid}/ask',json={'question':'Why does the token suffix get accepted?'})
    assert q.json()['memory_status']=='recalled'
    assert len(q.json()['memories'])==1
    f=client.post(f'/api/projects/{pid}/reflect',json={'question':'What did we learn from authentication?'})
    assert f.json()['provider']=='hindsight-reflect'


def test_bad_project_and_validation(client):
    assert client.get('/api/projects/notreal').status_code==404
    assert client.post('/api/import/github',json={'url':'https://evil.test/x'}).status_code==422 or client.post('/api/import/github',json={'url':'https://evil.test/x'}).status_code==400
    p=client.post('/api/demo').json()['id']
    assert client.post(f'/api/projects/{p}/ask',json={'question':'Hi'}).status_code==422


def test_zip_api(client):
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w') as z: z.writestr('source/main.py','print("hello")')
    r=client.post('/api/import/zip',files={'file':('demo.zip',buf.getvalue(),'application/zip')})
    assert r.status_code==200
    assert r.json()['stats']['files']==1
