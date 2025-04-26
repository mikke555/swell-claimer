from typing import Optional

from pydantic import BaseModel, Field


class Data(BaseModel):
    from_: str = Field(..., alias="from")
    to: str
    data: str
    value: str
    chainId: int
    gas: str
    maxFeePerGas: str
    maxPriorityFeePerGas: str


class Check(BaseModel):
    endpoint: str
    method: str


class Item(BaseModel):
    status: str
    data: Data
    check: Check


class Step(BaseModel):
    id: str
    action: str
    description: str
    kind: str
    items: list[Item]
    requestId: str
    depositAddress: str


class Currency(BaseModel):
    chainId: int
    address: str
    symbol: str
    name: str
    decimals: int


class Gas(BaseModel):
    currency: Currency
    amount: str
    amountFormatted: str
    amountUsd: str
    minimumAmount: str


class Currency1(BaseModel):
    chainId: int
    address: str
    symbol: str
    name: str
    decimals: int


class Relayer(BaseModel):
    currency: Currency1
    amount: str
    amountFormatted: str
    amountUsd: str
    minimumAmount: str


class Currency2(BaseModel):
    chainId: int
    address: str
    symbol: str
    name: str
    decimals: int


class RelayerGas(BaseModel):
    currency: Currency2
    amount: str
    amountFormatted: str
    amountUsd: str
    minimumAmount: str


class Currency3(BaseModel):
    chainId: int
    address: str
    symbol: str
    name: str
    decimals: int


class RelayerService(BaseModel):
    currency: Currency3
    amount: str
    amountFormatted: str
    amountUsd: str
    minimumAmount: str


class Currency4(BaseModel):
    chainId: int
    address: str
    symbol: str
    name: str
    decimals: int


class App(BaseModel):
    currency: Currency4
    amount: str
    amountFormatted: str
    amountUsd: str
    minimumAmount: str


class Fees(BaseModel):
    gas: Gas
    relayer: Relayer
    relayerGas: RelayerGas
    relayerService: RelayerService
    app: App


class Currency5(BaseModel):
    chainId: int
    address: str
    symbol: str
    name: str
    decimals: int


class CurrencyIn(BaseModel):
    currency: Currency5
    amount: str
    amountFormatted: str
    amountUsd: str
    minimumAmount: str


class Currency6(BaseModel):
    chainId: int
    address: str
    symbol: str
    name: str
    decimals: int


class CurrencyOut(BaseModel):
    currency: Currency6
    amount: str
    amountFormatted: str
    amountUsd: str
    minimumAmount: str


class TotalImpact(BaseModel):
    usd: str
    percent: str


class SwapImpact(BaseModel):
    usd: str
    percent: str


class Origin(BaseModel):
    usd: str
    value: str
    percent: str


class Destination(BaseModel):
    usd: str
    value: str
    percent: str


class SlippageTolerance(BaseModel):
    origin: Origin
    destination: Destination


class Details(BaseModel):
    operation: str
    sender: str
    recipient: str
    currencyIn: CurrencyIn
    currencyOut: CurrencyOut
    totalImpact: TotalImpact
    swapImpact: SwapImpact
    rate: str
    slippageTolerance: SlippageTolerance
    timeEstimate: int
    userBalance: str


class QuoteResponse(BaseModel):
    steps: Optional[list[Step]] = None
    fees: Optional[Fees] = None
    details: Optional[Details] = None
