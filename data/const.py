import json

import questionary

from models.network import Network

style = questionary.Style(
    [
        ("qmark", "fg:#47A6F9 bold"),
        ("pointer", "fg:#47A6F9 bold"),
        ("highlighted", "fg:#808080"),
        ("answer", "fg:#808080"),
        ("instruction", "fg:#808080 italic"),
    ]
)

ethereum = Network(
    name="ethereum",
    explorer="https://etherscan.io",
    eip_1559=True,
    native_token="ETH",
    id=1868,
)

swell = Network(
    name="swell",
    explorer="https://explorer.swellnetwork.io",
    eip_1559=True,
    native_token="ETH",
    id=1923,
)

linea = Network(
    name="linea",
    explorer="https://lineascan.build",
    eip_1559=True,
    id=59144,
    native_token="ETH",
)

optimism = Network(
    name="optimism",
    explorer="https://optimistic.etherscan.io",
    eip_1559=True,
    id=10,
    native_token="ETH",
)

base = Network(
    name="base",
    explorer="https://basescan.org",
    eip_1559=True,
    id=8453,
    native_token="ETH",
)

arbitrum = Network(
    name="arbitrum",
    explorer="https://arbiscan.io",
    eip_1559=True,
    id=42161,
    native_token="ETH",
)


network_mapping = {
    "ethereum": ethereum,
    "swell": swell,
    "linea": linea,
    "optimism": optimism,
    "base": base,
    "arbitrum": arbitrum,
}

MERKL_DISTRIBUTER = "0x3Ef3D8bA38EBe18DB133cEc108f4D14CE00Dd9Ae"

SWELL = "0x2826D136F5630adA89C1678b64A61620Aab77Aea"

with open("data/abi/ERC20.json") as f:
    ERC20_ABI = json.load(f)
