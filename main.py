from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import database
from api.routers import api_router


origins = [
    "http://localhost",
]

app = FastAPI()
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
