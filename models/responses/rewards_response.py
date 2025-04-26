from pydantic import BaseModel, RootModel


class ExplorerItem(BaseModel):
    id: str
    type: str
    url: str
    chainId: int


class Chain(BaseModel):
    id: int
    name: str
    icon: str
    Explorer: list[ExplorerItem]


class Token(BaseModel):
    address: str
    chainId: int
    symbol: str
    decimals: int


class Breakdown(BaseModel):
    reason: str
    amount: str
    claimed: str
    pending: str
    campaignId: str


class Reward(BaseModel):
    root: str
    recipient: str
    amount: str
    claimed: str
    pending: str
    proofs: list[str]
    token: Token
    breakdowns: list[Breakdown]


class ModelItem(BaseModel):
    chain: Chain
    rewards: list[Reward]


class RewardsResponse(RootModel):
    root: list[ModelItem]
