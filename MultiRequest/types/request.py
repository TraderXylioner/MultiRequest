from enum import Enum

from aiohttp import ClientResponse
from pydantic import BaseModel, ConfigDict

from .service import Service


class Method(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'


class Response(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    response_data: object | None = None
    response_object: ClientResponse | None = None


class Request(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    url: str
    method: Method
    params: dict | None = None
    headers: dict | None = None
    data: object | None = None
    service: Service
    metadata: dict | None = None
    response: Response | None = None

    def get_request_params(self):
        return {'url': self.url,
                'params': self.params,
                }
