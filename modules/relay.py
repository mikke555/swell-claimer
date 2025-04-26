import random

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed
from web3 import constants

import settings
from data.const import network_mapping
from models.network import Network
from models.responses.quote_response import QuoteResponse
from modules.http import HttpClient
from modules.logger import logger
from modules.utils import wei
from modules.wallet import Wallet


class PendingStatus(Exception):
    pass


class ReceiptNotAvailable(Exception):
    pass


class Relay(Wallet):
    BASE_URL = "https://api.relay.link"

    def __init__(
        self,
        id: str,
        private_key: str,
        chain_name: str,
        proxy: str = "",
        dest_chain_name: str = "",
        recipient: str | None = None,
    ):
        super().__init__(id, private_key, chain_name, proxy, recipient)
        self.http = HttpClient(self.proxy, self.BASE_URL)
        self.label += "Relay |"

        self.src_chain: Network = self.chain
        self.dest_chain: Network = network_mapping[dest_chain_name]

    @property
    def amount(self):
        return random.uniform(*settings.REFUEL_SETTINGS["refuel_amount"])

    def _quote(self) -> QuoteResponse:
        payload = {
            "user": self.address,
            "originChainId": self.chain.id,
            "destinationChainId": self.dest_chain.id,
            "originCurrency": constants.ADDRESS_ZERO,
            "destinationCurrency": constants.ADDRESS_ZERO,
            "recipient": self.address,
            "tradeType": "EXACT_INPUT",
            "amount": str(wei(self.amount)),
            "referrer": "relay.link/swap",
            "useExternalLiquidity": False,
            "useDepositAddress": False,
        }

        resp = self.http.post("/quote", json=payload)
        return QuoteResponse(**resp.json())

    def _verify_deposit(self, request_id: str) -> None:
        endpoint = f"/intents/status?requestId={request_id}"
        logger.info(f"{self.label} {self.http.base_url}{endpoint}")
        try:
            self._check_deposit_status(endpoint)
        except PendingStatus:
            raise Exception(f"Deposit not confirmed after max attempts")

    @retry(stop=stop_after_attempt(10), wait=wait_fixed(10), retry=retry_if_exception_type(PendingStatus))
    def _check_deposit_status(self, endpoint):
        resp = self.http.get(endpoint)
        data = resp.json()

        if "status" in data:
            status = data["status"]

            if data["status"] == "success":
                logger.debug(f"{self.label} Status <{status.upper()}>")
                return
            else:
                logger.info(f"{self.label} Status <{status.upper()}>")
                raise PendingStatus(f"Status is {status}")

    def _get_receipt(self, id: str) -> None:
        endpoint = f"/requests/v2?id={id}"
        try:
            self._check_receipt(endpoint)
        except ReceiptNotAvailable:
            raise Exception(f"Couldn't get a receipt after max attempts")

    @retry(stop=stop_after_attempt(10), wait=wait_fixed(10), retry=retry_if_exception_type(ReceiptNotAvailable))
    def _check_receipt(self, endpoint):
        resp = self.http.get(endpoint)
        data = resp.json()

        if "requests" in data:
            amount_usd = float(data["requests"][0]["data"]["metadata"]["currencyOut"]["amountUsd"])
            logger.debug(f"{self.label} ${amount_usd:.2f} in ETH received on {self.dest_chain.name.title()}\n")
            return
        else:
            logger.info(f"{self.label} Receipt not available yet")
            raise ReceiptNotAvailable("Receipt not available")

    def refuel(self) -> bool:
        quote = self._quote()

        if not quote.steps or not quote.steps[0].items:
            raise ValueError("Invalid quote response: missing steps or items")

        tx_data = quote.steps[0].items[0].data
        tx = {
            "from": self.address,
            "to": self.w3.to_checksum_address(tx_data.to),
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "chainId": self.chain.id,
            "value": int(tx_data.value),
            "data": tx_data.data,
            "gas": int(tx_data.gas),
            "maxFeePerGas": int(tx_data.maxFeePerGas),
            "maxPriorityFeePerGas": int(tx_data.maxPriorityFeePerGas),
        }

        tx_status = self.send_tx(
            tx,
            tx_label=f"{self.label} Refuel {self.amount:.6f} ETH {self.chain.name.title()} -> {self.dest_chain.name.title()}",
        )

        if tx_status:
            self._verify_deposit(quote.steps[0].requestId)
            self._get_receipt(quote.steps[0].requestId)
            return True

        return False
