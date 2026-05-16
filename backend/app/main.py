import uvicorn
from fastapi import FastAPI, APIRouter
from app.config import db
from contextlib import asynccontextmanager

def init_app():
    db.init()
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await db.create_all()
        
        yield
        
        await db.close()
        
    app= FastAPI(
        title="Download and Convert",
        description="Login Page",
        version="1",
        lifespan=lifespan
    )
        
    return app

app= init_app


def start():
    uvicorn.run("app.main:app", host="localhost",port=8888, reload=True)