import io
import zipfile
import pytest
from app.analysis import analyze
from app.demo_data import DEMO_FILES
from app.security import SourceFile, read_archive, InputError, parse_github_url

def makezip(files):
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w') as z:
        for name, content in files.items():z.writestr(name,content)
    return buf.getvalue()

def test_demo_has_architecture_and_modules():
    r=analyze(DEMO_FILES,'DemoAuth','demo:demoauth-v1')
    assert r['stats']['files']==len(DEMO_FILES)
    assert {'source':'src/api.py','target':'src/auth.py'} in r['edges']
    assert {'source':'src/auth.py','target':'src/config.py'} in r['edges']
    assert 'src/api.py' in r['entrypoints']
    assert 'flowchart LR' in r['mermaid']

def test_deterministic_project_id():
    a=analyze(DEMO_FILES,'test','github:user/repo')
    b=analyze(DEMO_FILES,'test','github:user/repo')
    assert a['id']==b['id']

def test_python_syntax_error_is_reported():
    a=analyze([SourceFile('broken.py','def broken(: pass')],'test','upload:broken')
    assert 'SyntaxError' in a['files'][0]['warnings'][0]

def test_zip_strips_root_folder():
    items=read_archive(makezip({'repo-123/src/main.py':'print(1)','repo-123/README.md':'Hello'}))
    assert {item.path for item in items} == {'src/main.py','README.md'}

def test_zip_rejects_traversal():
    with pytest.raises(InputError): read_archive(makezip({'../bad.py':'x=1'}))

def test_zip_ignores_secrets_and_dependencies():
    items=read_archive(makezip({'repo/src/app.py':'x=1','repo/.env':'TOKEN=secret','repo/node_modules/dep.js':'x=2'}))
    assert [i.path for i in items]==['src/app.py']

def test_empty_zip_rejected():
    with pytest.raises(InputError): read_archive(makezip({'foo/secret.env':'x'}))

def test_github_url_restricts_hosts():
    assert parse_github_url('https://github.com/acme/service')==('acme','service')
    with pytest.raises(InputError):parse_github_url('http://localhost:8000/a')
    with pytest.raises(InputError):parse_github_url('https://github.com.evil.test/a/b')

def test_js_scanning_resolves_import():
    files=[SourceFile('src/index.ts',"import {x} from './util'; x()"),SourceFile('src/util.ts','export function x() {}')]
    r=analyze(files,'js','js')
    assert {'source':'src/index.ts','target':'src/util.ts'} in r['edges']
