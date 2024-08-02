from enum import Enum

from pydantic import BaseModel


class Protocol(Enum):
    HTTP = 'HTTP'
    HTTPS = 'HTTPS'


class Proxy(BaseModel):
    protocol: Protocol
    ip: str
    port: int
    user: str | None = None
    password: str | None = None

    def to_string(self):
        if self.user:
            return f'{self.protocol.value.lower()}://{self.user}:{self.password}@{self.ip}:{self.port}'
        else:
            return f'{self.protocol.value.lower()}://{self.ip}:{self.port}'

    def __eq__(self, other):
        if isinstance(other, Proxy):
            return self.ip + str(self.port) == other.ip + str(self.port)
        return False

    def __hash__(self):
        return hash(self.ip + str(self.port))
