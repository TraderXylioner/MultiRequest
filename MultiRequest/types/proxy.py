from enum import Enum

from pydantic import BaseModel


class Protocol(Enum):
    HTTP = 'HTTP'
    HTTPS = 'HTTPS'


class Proxy(BaseModel):
    protocol: Protocol
    ip: str
    port: int | None = None
    user: str | None = None
    password: str | None = None
