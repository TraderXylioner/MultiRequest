from pydantic import BaseModel

from .service import Service


class Request(BaseModel):
    url: str
    service: Service
    response: dict | None = None
