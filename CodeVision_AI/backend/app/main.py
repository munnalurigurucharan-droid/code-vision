from __future__ import annotations
import hashlib
import re
from pathlib import PurePosixPath
from urllib.parse import quote
import httpx
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .config import settings
from .security import read_archive, parse_github_url, InputError, MAX_ARCHIVE_SIZE
from .store import ProjectStore
from .analysis import analyze
from .assistant import investigate
from .memory import MemoryService, HindsightError
from .demo_data import DEMO_FILES, DEMO_INCIDENT

app = FastAPI(title='CodeVision AI', version='1.0.0', description='Static code intelligence and real Hindsight project memory')
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.frontend_origin.split(',') if x.strip()],
                   allow_credentials=False, allow_methods=['GET','POST'], allow_headers=['Content-Type'])
store = ProjectStore(settings.database_file)
memory = MemoryService(settings)

class GithubImport(BaseModel):
    url: str = Field(min_length=20,max_length=250)

class AskRequest(BaseModel):
    question: str = Field(min_length=5,max_length=2000)
    use_memory: bool = True

class ResolutionRequest(BaseModel):
    issue: str = Field(min_length=8,max_length=2000)
    root_cause: str = Field(min_length=8,max_length=2000)
    fix: str = Field(min_length=8,max_length=3000)
    failed_attempts: str = Field(default='',max_length=1600)

class ReflectRequest(BaseModel):
    question: str = Field(min_length=5,max_length=1000)

def get_project(pid: str) -> dict:
    project = store.get(pid)
    if project is None: raise HTTPException(status_code=404, detail='Project not found; import a repository first.')
    return project

def store_project(files, title, origin) -> dict:
    project = analyze(files,title=title,origin=origin)
    store.put(project)
    return project

@app.get('/api/health')
def health():
    return {'status':'ok','application':'CodeVision AI','hindsight_configured':memory.configured,
            'hindsight_verified':False,'groq_configured':bool(settings.groq_api_key),
            'mode':'full integrations require real Hindsight and Groq credentials'}

@app.get('/api/projects')
def projects():
    return store.list()

@app.post('/api/demo')
def create_demo():
    project = store_project(DEMO_FILES,'DemoAuth — synthetic sample','demo:demoauth-v1')
    return project

@app.post('/api/import/zip')
async def import_zip(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith('.zip'):
        raise HTTPException(status_code=400,detail='Select a .zip file.')
    data = await file.read(MAX_ARCHIVE_SIZE+1)
    try:
        sources = read_archive(data)
    except InputError as e:
        raise HTTPException(status_code=400,detail=str(e)) from e
    digest=hashlib.sha256(data).hexdigest()[:20]
    return store_project(sources, PurePosixPath(file.filename).stem[:90], f'upload:{digest}')

@app.post('/api/import/github')
async def import_github(body: GithubImport):
    try:
        owner, repo = parse_github_url(body.url)
    except InputError as e:
        raise HTTPException(status_code=400,detail=str(e)) from e
    try:
        async with httpx.AsyncClient(timeout=25, follow_redirects=False) as client:
            response = await client.get(f'https://api.github.com/repos/{owner}/{repo}', headers={'Accept':'application/vnd.github+json','User-Agent':'CodeVision-Hackathon'})
            response.raise_for_status()
            meta = response.json()
            if meta.get('private'): raise HTTPException(status_code=400,detail='Only public repositories are supported.')
            branch = str(meta.get('default_branch','main'))
            if not re.fullmatch(r'[a-zA-Z0-9_./-]{1,150}',branch):
                raise HTTPException(status_code=400,detail='Unsupported default branch name.')
            archive_url=f'https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{quote(branch, safe="/")}'
            async with client.stream('GET',archive_url) as zipped:
                zipped.raise_for_status()
                parts=[]; size=0
                async for chunk in zipped.aiter_bytes():
                    size+=len(chunk)
                    if size > MAX_ARCHIVE_SIZE: raise HTTPException(status_code=413,detail='Repository ZIP exceeds 12 MB. Upload a smaller subset.')
                    parts.append(chunk)
                raw=b''.join(parts)
        sources=read_archive(raw)
    except HTTPException: raise
    except InputError as e:
        raise HTTPException(status_code=400,detail=str(e)) from e
    except (httpx.TimeoutException, httpx.HTTPStatusError, httpx.RequestError) as e:
        raise HTTPException(status_code=502,detail=f'GitHub fetch failed ({type(e).__name__}). Try a ZIP.') from e
    return store_project(sources, f'{owner}/{repo}', f'github:{owner.lower()}/{repo.lower()}')

@app.get('/api/projects/{pid}')
def project_details(pid: str):
    return get_project(pid)

@app.get('/api/projects/{pid}/resolutions')
def list_resolutions(pid: str):
    get_project(pid)
    return store.resolutions(pid)

@app.post('/api/projects/{pid}/resolutions')
async def remember_resolution(pid: str, body: ResolutionRequest):
    project=get_project(pid)
    narrative=(f"Repository {project['title']} ({project['origin']}).\n"
               f"RESOLVED INCIDENT: {body.issue}\nROOT CAUSE: {body.root_cause}\n"
               f"VERIFIED OR PROPOSED FIX AS REPORTED BY DEVELOPER: {body.fix}\n"
               f"FAILED ATTEMPTS: {body.failed_attempts or 'None reported'}\n"
               "This is developer-supplied historical context, not an independently verified fix.")
    try:
        await memory.retain(pid,narrative)
    except HindsightError as e:
        raise HTTPException(status_code=503,detail=str(e)) from e
    # Never log a resolution as persisted memory until real retain succeeded.
    store.log_resolution(pid,body.issue,body.root_cause,body.fix,body.failed_attempts)
    return {'stored_in_hindsight':True,'bank_id':memory.bank(pid),'message':'Hindsight retained the developer-reported resolution.'}

@app.post('/api/projects/{pid}/demo/remember')
async def remember_demo(pid: str):
    project=get_project(pid)
    if project['origin'] != 'demo:demoauth-v1':
        raise HTTPException(status_code=400,detail='Sample seeding is only available for the built-in synthetic demo.')
    return await remember_resolution(pid,ResolutionRequest(**DEMO_INCIDENT))

@app.post('/api/projects/{pid}/ask')
async def ask(pid: str, body: AskRequest):
    project=get_project(pid)
    retrieved=[]
    status='disabled' if not body.use_memory else 'not-configured'
    if body.use_memory and memory.configured:
        try:
            retrieved=await memory.recall(pid,body.question)
            status='recalled' if retrieved else 'no-results'
        except HindsightError as e:
            status='error'; error=str(e)
        else: error=None
    else: error=None
    answer, provider=await investigate(project,body.question,retrieved,settings)
    return {'answer':answer,'provider':provider,'memory_status':status,'memories':retrieved,
            'memory_error':error,'bank_id':memory.bank(pid),'question':body.question,
            'disclaimer':'Static code inspection and developer-reported history; not a reproduced bug or verified fix.'}

@app.post('/api/projects/{pid}/reflect')
async def reflect(pid: str, body: ReflectRequest):
    get_project(pid)
    try:
        text=await memory.reflect(pid,body.question)
    except HindsightError as e:
        raise HTTPException(status_code=503,detail=str(e)) from e
    return {'answer':text,'provider':'hindsight-reflect','bank_id':memory.bank(pid)}
