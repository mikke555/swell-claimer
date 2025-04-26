from data.const import MERKL_DISTRIBUTER
from models.responses.claim_response import ClaimResponse
from models.responses.rewards_response import RewardsResponse
from modules.http import HttpClient
from modules.logger import logger
from modules.wallet import Wallet


class Merkl(Wallet):
    def __init__(self, id: str, private_key: str, chain_name: str, proxy: str = "", recipient: str | None = None):
        super().__init__(id, private_key, chain_name, proxy, recipient)
        self.http = HttpClient(self.proxy)
        self.label += "Merkl |"

    def get_proofs(self, id: int = 1923) -> RewardsResponse | None:
        url = f"https://api.merkl.xyz/v4/users/{self.address}/rewards?chainId={id}"

        resp = self.http.get(url)
        data = RewardsResponse(resp.json())

        if not data.root:
            logger.warning(f"{self.label} No Swell rewards found for this address")

        return data

    def get_claim_data(self) -> ClaimResponse | None:
        url = f"https://app.merkl.xyz/transaction/claim"

        rewards_data = self.get_proofs()

        if not rewards_data.root:
            return

        proofs = rewards_data.root[0].rewards[0].proofs
        distributor = self.w3.to_checksum_address(rewards_data.root[0].rewards[0].token.address)
        amount = rewards_data.root[0].rewards[0].amount
        claimed_amount = rewards_data.root[0].rewards[0].claimed
        decimals = rewards_data.root[0].rewards[0].token.decimals

        if claimed_amount != "0":
            logger.warning(f"{self.label} Already claimed {int(claimed_amount) / 10**decimals} Swell")
            return

        logger.debug(f"{self.label} Eligible for {int(amount) / 10**decimals} Swell")

        payload = {
            "userAddress": self.address,
            "distributor": distributor,
            "args": [[self.address], [distributor], [amount], [proofs]],
            "sponsor": False,
        }

        resp = self.http.post(url, json=payload)
        return ClaimResponse(**resp.json())

    def claim(self, claim_data: ClaimResponse | None = None):
        if claim_data is None:
            return

        tx_params = self.get_tx_params(to=MERKL_DISTRIBUTER, data=claim_data.data, get_gas=True)
        self.send_tx(tx_params, tx_label=f"{self.label} Claim rewards")
