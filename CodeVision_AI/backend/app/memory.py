"""Only real Hindsight can provide a memory success; no simulated memory responses."""
from __future__ import annotations
import hashlib
from .config import Settings

class HindsightError(RuntimeError):
    pass

class MemoryService:
    def __init__(self, settings: Settings, client=None):
        self.settings = settings
        self.client = client

    @property
    def configured(self) -> bool:
        url = self.settings.hindsight_base_url
        return bool(self.client or (url.startswith(('http://localhost', 'http://127.0.0.1')) or self.settings.hindsight_api_key.strip()))

    def _get(self):
        if self.client is not None:
            return self.client
        if not self.configured:
            raise HindsightError('Hindsight not configured. Add HINDSIGHT_API_KEY to .env.')
        url = self.settings.hindsight_base_url.strip().rstrip('/')
        if not (url.startswith('https://') or url.startswith('http://localhost') or url.startswith('http://127.0.0.1')):
            raise HindsightError('Hindsight requires HTTPS, except local development.')
        try:
            from hindsight_client import Hindsight
        except ImportError as exc:
            raise HindsightError('Install backend/requirements.txt for official Hindsight SDK.') from exc
        self.client = Hindsight(base_url=url, api_key=self.settings.hindsight_api_key or None, timeout=45.0)
        return self.client

    def bank(self, project_id: str) -> str:
        return f'codevision-{hashlib.sha256(project_id.encode()).hexdigest()[:18]}'

    async def retain(self, project_id: str, content: str) -> None:
        try:
            await self._get().aretain(bank_id=self.bank(project_id), content=content)
        except HindsightError: raise
        except Exception as exc:
            raise HindsightError(f'Live Hindsight retain failed ({type(exc).__name__}); check key, credits, server logs.') from exc

    async def recall(self, project_id: str, query: str) -> list[dict]:
        try:
            result = await self._get().arecall(bank_id=self.bank(project_id), query=query)
            records = getattr(result,'results',None)
            if records is None and isinstance(result,dict): records = result.get('results',[])
            if records is None: raise HindsightError('Unexpected Hindsight recall payload.')
            output = []
            for record in list(records)[:6]:
                content = (record.get('text','') if isinstance(record,dict) else getattr(record,'text',''))
                source = (record.get('id','') if isinstance(record,dict) else getattr(record,'id',''))
                if content: output.append({'text':str(content)[:1400], 'id':str(source or '')})
            return output
        except HindsightError: raise
        except Exception as exc:
            raise HindsightError(f'Live Hindsight recall failed ({type(exc).__name__}); check key, credits, server logs.') from exc

    async def reflect(self, project_id: str, query: str) -> str:
        try:
            result = await self._get().areflect(bank_id=self.bank(project_id), query=query)
            text = result.get('text','') if isinstance(result,dict) else getattr(result,'text','')
            if not text: raise HindsightError('Hindsight reflect produced no answer.')
            return str(text)[:4000]
        except HindsightError: raise
        except Exception as exc:
            raise HindsightError(f'Live Hindsight reflect failed ({type(exc).__name__}); check key, credits, server logs.') from exc
