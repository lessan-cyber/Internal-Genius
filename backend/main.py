# from typing import Union
import logging
import sys
from fastapi import FastAPI
from config import setup_logging
from repositories import VectorStoreRepository
from contextlib import asynccontextmanager
from settings import settings
from api import document_router

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    vector_store_repository = VectorStoreRepository()
    if not vector_store_repository.health_check():
        logging.error("Failed to connect to ChromaDB. Please check the connection.")
        sys.exit(1)
    logging.info("Successfully connected to ChromaDB.")

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(document_router, prefix="/api/documents", tags=["documents"])


@app.get("/")
async def read_root():
    return {"Hello": "from Internal Genius"}
