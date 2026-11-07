import os
from pathlib import Path
import tempfile
import pytest
from fastapi.testclient import TestClient

# Environment must be supplied before importing the app/settings.
os.environ['DATABASE_PATH'] = str(Path(tempfile.gettempdir()) / 'codevision-hackathon-test.sqlite3')
os.environ['HINDSIGHT_API_KEY'] = ''
os.environ['GROQ_API_KEY'] = ''
from app.main import app, store

@pytest.fixture
def client():
    with store.connect() as con:
        con.execute('DELETE FROM resolutions')
        con.execute('DELETE FROM projects')
    with TestClient(app) as c:
        yield c
