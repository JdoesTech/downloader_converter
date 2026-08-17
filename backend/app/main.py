from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS, dispose_db, init_db, create_all_tables
from app.controller import authentication, users
from app.services.auth_service import generate_role


def init_app() -> FastAPI:
    init_db()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await create_all_tables()
        await generate_role()
        yield
        await dispose_db()

    app = FastAPI(
        title="Download and Convert",
        description="Authentication and file utilities API",
        version="1",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(authentication.router)
    app.include_router(users.router)
    return app


app = init_app()


def start() -> None:
    uvicorn.run("app.main:app", host="localhost", port=8888, reload=True)
