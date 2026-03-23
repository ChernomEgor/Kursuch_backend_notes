import uvicorn

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import engine
from db.models import Base


from routers.auth_router import router as auth_router
from routers.note_router import router as note_router

from services.token_service import security

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "https://nothishit.github.io", "https://quickly-benevolent-moose.cloudpub.ru"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(note_router)


security.handle_errors(app)



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)