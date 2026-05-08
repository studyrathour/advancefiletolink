from fastapi import FastAPI

app = FastAPI()

from .stream_routes import app as router

__all__ = ["app"]