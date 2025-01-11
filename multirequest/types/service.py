from pydantic import BaseModel


class Service(BaseModel):
    name: str
    rate_limit: int
