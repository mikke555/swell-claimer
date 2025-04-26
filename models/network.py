from pydantic import BaseModel


class Network(BaseModel):
    name: str
    explorer: str
    eip_1559: bool
    native_token: str
    id: int

    def __str__(self):
        return self.name
