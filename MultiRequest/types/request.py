from aiohttp import ClientResponse
from pydantic import BaseModel, ConfigDict

from .service import Service


class Request(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    url: str
    service: Service
    name: str | None = None
    data: object | None = None
    response_object: ClientResponse | None = None
