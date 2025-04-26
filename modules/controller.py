import random

import settings
from data.const import SWELL
from models.account import Account
from modules.merkl import Merkl
from modules.relay import Relay
from modules.utils import random_sleep, wei
from modules.wallet import Wallet


class Controller:
    def __init__(self, account: Account, action: str):
        self.action = action
        self.account = account.model_dump()
        self.min_balance = wei(settings.REFUEL_SETTINGS["min_balance"])
        self.min_src_balance = wei(max(settings.REFUEL_SETTINGS["refuel_amount"]))

    def execute(self) -> None:
        handler = getattr(self, self.action)
        handler()

    def check_swell(self) -> None:
        merkl = Merkl(**self.account, chain_name="swell")
        merkl.get_claim_data()

    def claim_swell(self) -> None:
        merkl = Merkl(**self.account, chain_name="swell")

        if merkl.get_balance(SWELL) and settings.SEND_TO_EXCHANGE:
            merkl.transfer_token(SWELL)
            return

        claim_data = merkl.get_claim_data()
        if not claim_data:
            return

        if merkl.get_balance() < self.min_balance:
            self._refuel(dest="swell")
            random_sleep(*settings.SLEEP_BETWEEN_ACTIONS)

        merkl.claim(claim_data)

        if settings.SEND_TO_EXCHANGE:
            random_sleep(*settings.SLEEP_BETWEEN_ACTIONS)
            merkl.transfer_token(SWELL)

    def _get_balance_for_chain(self, chain: str) -> float:
        """Get ETH balance for a specific chain."""

        wallet = Wallet(**self.account, chain_name=chain)
        return wallet.get_balance()

    def _get_rand_refuel_src(self):
        src_chains = settings.REFUEL_SETTINGS["chains"].copy()
        random.shuffle(src_chains)

        balances = {chain: self._get_balance_for_chain(chain) for chain in src_chains}

        for chain in src_chains:
            if balances[chain] > self.min_src_balance:
                return chain
        raise Exception("No source chain with sufficient balance")

    def _refuel(self, dest: str) -> bool:
        src = self._get_rand_refuel_src()
        relay = Relay(**self.account, chain_name=src, dest_chain_name=dest)

        return relay.refuel()
