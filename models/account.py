from pydantic import BaseModel


class Account(BaseModel):
    id: str
    private_key: str
    proxy: str | None
    recipient: str | None
