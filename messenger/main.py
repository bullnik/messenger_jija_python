import asyncio

from fastapi import FastAPI
import uvicorn

from endpoints.login import router as login_router
from endpoints.user import router as user_router
from endpoints.utils import router as utils_router
from messenger.core.db.models import Base
from messenger.schemas.consumer import consume

app = FastAPI()

app.include_router(user_router, tags=["user"])
app.include_router(login_router, tags=["login"])
app.include_router(utils_router, tags=["utils"])

@app.get('/')
async def hello():
    return {'message': 'Hello world!'}


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    uvicorn.run('main:app', host='0.0.0.0', port=8080, reload=True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume(hostname="localhost", port="80"))
    loop.run_forever()
