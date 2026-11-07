from fastapi import FastAPI, Header, HTTPException
from src.auth import authorize
app = FastAPI(title='DemoAuth')

@app.get('/private')
def private_route(authorization: str = Header(default='')):
    if not authorize(authorization.removeprefix('Bearer ')):
        raise HTTPException(status_code=401, detail='Invalid token')
    return {'message':'authorized'}
