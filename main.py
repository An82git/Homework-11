from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter
from fastapi import FastAPI
import redis.asyncio as redis
import uvicorn

from src.routes import auth, contacts, users
from src.conf.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Asynchronous context manager for setting up lifespan events.

    :param app: FastAPI application instance.
    :type app: FastAPI
    """
    r = await redis.Redis(
        host = settings.redis_host,
        port = settings.redis_port
    )
    await FastAPILimiter.init(r)
    yield


app = FastAPI(lifespan=lifespan)


origins = [ 
    "*"
    ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contacts.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')


@app.get("/")
def read_root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
