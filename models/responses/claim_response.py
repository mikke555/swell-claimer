from typing import Optional

from pydantic import BaseModel, Field


class ClaimResponse(BaseModel):
    to: Optional[str] = None
    from_: Optional[str] = Field(None, alias="from")
    data: Optional[str] = None
