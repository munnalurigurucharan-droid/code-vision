"""Static, bounded analysis: the repository is not imported or executed."""
from __future__ import annotations
import ast
import hashlib
import re
from collections import Counter
from pathlib import PurePosixPath
from .security import SourceFile

PY_EXTS = {'.py'}
JS_EXTS = {'.js', '.jsx', '.ts', '.tsx'}
IMPORT_JS = re.compile(r'''(?:import\s+(?:[^;\n]*?\s+from\s+)?|require\s*\()\s*['\"]([^'\"]+)['\"]''')
FRAMEWORK = {"fastapi":"FastAPI", "django":"Django", "flask":"Flask", "react":"React", "next":"Next.js", "express":"Express", "streamlit":"Streamlit", "pytest":"pytest", "pydantic":"Pydantic"}

def language(path: str) -> str:
    suf = PurePosixPath(path).suffix.lower()
    return 'Python' if suf == '.py' else 'JavaScript/TypeScript' if suf in JS_EXTS else 'Config / docs'

def _parse_python(path: str, text: str) -> dict:
    imports, symbols, warnings, call_names = [], [], [], []
    try:
        tree = ast.parse(text, filename=path)
    except SyntaxError as e:
        return {'imports': [], 'symbols': [], 'calls': [], 'warnings': [f'SyntaxError at line {e.lineno}: {e.msg}'], 'entrypoint': False}
    lines = text.splitlines()
    entrypoint = path.endswith(('main.py','app.py','manage.py','__main__.py','server.py','api.py')) or bool(re.search(r'\bapp\s*=\s*(FastAPI|Flask)\s*\(', text))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(x.name for x in node.names)
        elif isinstance(node, ast.ImportFrom):
            prefix = '.' * node.level
            mod = node.module or ''
            imports.append(prefix + mod)
            if not mod:
                imports.extend(prefix + x.name for x in node.names)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            kind = 'class' if isinstance(node, ast.ClassDef) else 'async function' if isinstance(node, ast.AsyncFunctionDef) else 'function'
            symbols.append({'name': node.name, 'kind':kind, 'line': node.lineno, 'doc': (ast.get_docstring(node) or '')[:140]})
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                call_names.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                call_names.append(node.func.attr)
        elif isinstance(node, ast.Compare):
            # Detect if __name__ == '__main__' without running source
            chunk = ast.get_source_segment(text, node) or ''
            if '__name__' in chunk and '__main__' in chunk:
                entrypoint = True
    if 'eval(' in text or 'exec(' in text:
        warnings.append('Review dynamic execution: eval/exec reference found (heuristic).')
    for number, line in enumerate(lines, 1):
        if ('TODO' in line or 'FIXME' in line) and len(warnings) < 8:
            warnings.append(f'Line {number}: {line.strip()[:110]}')
    return {'imports': list(dict.fromkeys(imports)), 'symbols':symbols[:45], 'calls':Counter(call_names).most_common(12), 'warnings':warnings, 'entrypoint':entrypoint}

def _parse_js(path: str, text: str) -> dict:
    imports = list(dict.fromkeys(IMPORT_JS.findall(text)))
    names = re.findall(r'(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)|(?:export\s+)?class\s+([A-Za-z_$][\w$]*)', text)
    symbols = [{'name': a or b, 'kind': 'function' if a else 'class', 'line': text[:text.find(a or b)].count('\n') + 1} for a,b in names[:40]]
    return {'imports':imports, 'symbols':symbols, 'calls':[], 'warnings':['JS/TS imports are inspected with a lightweight scanner, not a full parser.'], 'entrypoint':path.endswith(('main.ts','main.tsx','main.js','index.js','index.ts','server.js','app.js','App.tsx'))}

def _target(source: str, imported: str, existing: set[str]) -> str | None:
    if not imported: return None
    source_dir = list(PurePosixPath(source).parent.parts)
    if source_dir == ['.']: source_dir = []
    if imported.startswith(('./','../')):
        # JS local module resolution
        base = source_dir[:]
        segments = imported.split('/')
        while segments and segments[0] in ('.','..'):
            if segments[0] == '..' and base: base.pop()
            segments.pop(0)
        name = '/'.join(segments)
    elif imported.startswith('.'):
        # Python: single dot means from same package, double dot means parent.
        levels = len(imported) - len(imported.lstrip('.'))
        base = source_dir[:max(0,len(source_dir)-(levels-1))]
        name = imported[levels:].replace('.', '/')
    else:
        base = []
        name = imported.replace('.', '/')
    rel = '/'.join([*base, name]).strip('/')
    candidates = [rel, rel+'.py', rel+'/__init__.py', rel+'/index.ts', rel+'/index.tsx', rel+'/index.js', rel+'.ts', rel+'.tsx', rel+'.js', rel+'.jsx']
    for candidate in candidates:
        if candidate in existing and candidate != source:
            return candidate
    return None

def analyze(files: list[SourceFile], title: str, origin: str) -> dict:
    source = sorted(files, key=lambda f:f.path)
    # Identity remains stable per origin, allowing cross-session, per-repo Hindsight memory.
    canonical = origin.strip().lower()
    project_id = hashlib.sha256(canonical.encode()).hexdigest()[:16]
    paths = {f.path for f in source}
    items = []
    imported_edges = set()
    frameworks = set()
    for f in source:
        parsed = _parse_python(f.path, f.text) if f.path.endswith('.py') else _parse_js(f.path, f.text) if PurePosixPath(f.path).suffix in JS_EXTS else {'imports':[],'symbols':[],'calls':[],'warnings':[],'entrypoint':False}
        imports = parsed['imports']
        for imp in imports:
            top = imp.split('.')[0].split('/')[0].lower()
            if top in FRAMEWORK: frameworks.add(FRAMEWORK[top])
            target = _target(f.path, imp, paths)
            if target: imported_edges.add((f.path,target))
        item = {'path':f.path, 'language':language(f.path), 'lines':len(f.text.splitlines()),
                'imports':imports[:30], 'symbols':parsed['symbols'], 'calls':parsed['calls'],
                'warnings':parsed['warnings'], 'entrypoint':parsed['entrypoint'],
                'preview': f.text[:3200]}
        items.append(item)
    # infer entrypoints, mark as heuristics, not an actual runtime trace
    entrypoints = [x['path'] for x in items if x['entrypoint']]
    if not entrypoints:
        entrypoints = [f.path for f in source if f.path.lower().endswith(('readme.md','package.json','pyproject.toml'))][:2]
    paths_for_diagram = [f for f in source if f.path.endswith(('.py','.ts','.tsx','.js','.jsx'))]
    paths_for_diagram = paths_for_diagram[:28]
    diagram_set = {x.path for x in paths_for_diagram}
    node_ids = {path:f'n{i}' for i,path in enumerate(sorted(diagram_set))}
    # Mermaid diagrams use opaque ids and quote-escaped labels, not raw code as syntax.
    mermaid = ['flowchart LR']
    for path, nid in node_ids.items():
        clean = path.replace('"', "'").replace('<','').replace('>','')[:64]
        mermaid.append(f'  {nid}["{clean}"]')
    for a,b in sorted(imported_edges):
        if a in node_ids and b in node_ids:
            mermaid.append(f'  {node_ids[a]} --> {node_ids[b]}')
    counts = Counter(x['language'] for x in items)
    problem_count = sum(len(x['warnings']) for x in items if x['language']=='Python')
    return {'id':project_id, 'title':title[:120], 'origin':origin,
        'stats':{'files':len(items),'lines':sum(x['lines'] for x in items), 'dependencies':len(imported_edges), 'warnings':problem_count},
        'frameworks':sorted(frameworks), 'languages':dict(counts), 'entrypoints':entrypoints[:10],
        'files':items, 'edges':[{'source':a,'target':b} for a,b in sorted(imported_edges)],
        'mermaid':'\n'.join(mermaid),
        'flow':([{'step':i+1,'title':t,'description':d} for i,(t,d) in enumerate([
            ('Entry candidates',f"Possible start files: {', '.join(entrypoints[:3]) or 'not detected'}"),
            ('Module dependencies',f"Resolved {len(imported_edges)} internal import links statically"),
            ('Application behavior','Inspect functions and call sites; exact runtime order requires dynamic tracing'),
            ('Hindsight memory','Previous debugging outcomes are retrieved from the per-repository memory bank')
        ])]),
        'limitations':['Imports and file relationships are static, not a runtime trace.',
        'Python uses AST; JavaScript/TypeScript uses a lightweight import scanner.',
        'No repository code is executed. External library dependencies may be unresolved.',
        'Generated explanations and troubleshooting suggestions require human verification.']}
