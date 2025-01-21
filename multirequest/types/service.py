from pydantic import BaseModel


class Service(BaseModel):
    name: str
    rate_limit: int
    time_to_update: int = 1


    def __hash__(self):
        return hash(self.name)
