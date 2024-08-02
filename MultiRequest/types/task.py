from pydantic import BaseModel

from .request import Request


class Task(BaseModel):
    requests: list[Request]
