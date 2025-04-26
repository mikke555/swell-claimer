import random
import time
from datetime import datetime
from decimal import Decimal

from tqdm import tqdm
from web3 import Web3

import settings
from models.account import Account


def read_file(path: str, prefix: str = "") -> list[str]:
    with open(path) as f:
        return [prefix + line.strip() for line in f if line.strip()]


def get_accounts() -> list[Account]:
    keys = read_file("input_data/keys.txt")
    proxies = read_file("input_data/proxies.txt", prefix="http://")

    if settings.SEND_TO_EXCHANGE:
        recipients = read_file("input_data/recipients.txt")

        if len(keys) != len(recipients):
            raise ValueError("Number of keys and recipients must be the same")
    else:
        recipients = None

    pairs = [
        (
            key,
            proxies[i % len(proxies)] if settings.USE_PROXY else None,
            recipients[i] if settings.SEND_TO_EXCHANGE else None,
        )
        for i, key in enumerate(keys)
    ]

    if settings.SHUFFLE_KEYS:
        random.shuffle(pairs)

    accounts = [
        Account(id=f"[{index}/{len(keys)}]", private_key=key, proxy=proxy, recipient=recipient)
        for index, (key, proxy, recipient) in enumerate(pairs, start=1)
    ]

    return accounts


def random_sleep(max_time: int, min_time: int = 1) -> None:
    if min_time > max_time:
        min_time, max_time = max_time, min_time

    x = random.randint(min_time, max_time)
    time.sleep(x)


def sleep(from_sleep: int, to_sleep: int) -> None:
    x = random.randint(from_sleep, to_sleep)
    desc = datetime.now().strftime("%H:%M:%S")

    for _ in tqdm(range(x), desc=desc, bar_format="{desc} | Sleeping {n_fmt}/{total_fmt}"):
        time.sleep(1)
    print()


def wei(value: float) -> int:
    return Web3.to_wei(value, "ether")


def ether(value: int) -> Decimal:
    return Web3.from_wei(value, "ether")
