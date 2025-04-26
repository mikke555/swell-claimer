from eth_account import Account
from eth_account.datastructures import SignedTransaction
from eth_account.messages import encode_defunct
from eth_account.signers.local import LocalAccount
from eth_typing import ChecksumAddress
from web3 import HTTPProvider, Web3
from web3.contract import Contract
from web3.exceptions import Web3Exception, Web3RPCError
from web3.middleware import ExtraDataToPOAMiddleware
from web3.types import TxParams, TxReceipt, Wei

import settings
from data.const import ERC20_ABI, network_mapping
from models.network import Network
from modules.logger import logger


class Wallet:
    id: str
    account: LocalAccount
    address: ChecksumAddress
    proxy: str
    chain: Network
    w3: Web3
    recipient: str | None

    def __init__(
        self, id: str, private_key: str, chain_name: str, proxy: str = "", recipient: str | None = None
    ) -> None:
        self.id = id
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        self.proxy = proxy
        self.chain = network_mapping[chain_name]
        self.w3 = self.get_web3(chain_name)
        self.recipient = self.w3.to_checksum_address(recipient) if recipient else None

        if settings.TRUNCATE_ADDRESS_IN_LOGS:
            self.label = f"{id} {self.address[:6]}...{self.address[-4:]} | "
        else:
            self.label = f"{id} {self.address} | "

    def get_web3(self, chain_name: str) -> Web3:
        web3 = Web3(HTTPProvider(settings.RPC_LIST[chain_name]))
        web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        return web3

    def get_contract(self, contract_address: str, abi: dict | None = None) -> Contract:
        address = Web3.to_checksum_address(contract_address)

        if not abi:
            abi = ERC20_ABI

        return self.w3.eth.contract(address=address, abi=abi)

    def get_balance(self, token_address: str = "", human: bool = False) -> int | float:
        if token_address:
            token = self.get_contract(token_address)
            balance = token.functions.balanceOf(self.address).call()
            decimals = token.functions.decimals().call()
        else:
            balance = self.w3.eth.get_balance(self.address)
            decimals = 18

        if human:
            return balance / 10**decimals

        return balance

    def get_token_info(self, token_address: str) -> dict:
        token: Contract = self.get_contract(token_address)
        name: str = token.functions.name().call()
        symbol: str = token.functions.symbol().call()
        decimals: int = token.functions.decimals().call()
        balance: int = token.functions.balanceOf(self.address).call()

        return {"name": name, "symbol": symbol, "decimals": decimals, "balance": balance}

    def get_gas(self, tx: TxParams) -> TxParams:
        if self.chain.eip_1559:
            latest_block = self.w3.eth.get_block("latest")
            base_fee = int(latest_block.get("baseFeePerGas", 0))
            max_priority_fee = self.w3.eth.max_priority_fee
            max_fee_per_gas = max_priority_fee + base_fee

            tx["maxFeePerGas"] = Wei(max_fee_per_gas)
            tx["maxPriorityFeePerGas"] = Wei(max_priority_fee)

        else:
            tx["gasPrice"] = self.w3.eth.gas_price

        tx["gas"] = self.w3.eth.estimate_gas(tx)
        return tx

    def get_tx_params(self, value: int = 0, get_gas: bool = False, **kwargs) -> TxParams:
        params = {
            "chainId": self.chain.id,
            "from": self.address,
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "value": value,
            **kwargs,
        }

        return self.get_gas(TxParams(**params)) if get_gas else TxParams(**params)

    def sign_message(self, message: str) -> str:
        message_encoded = encode_defunct(text=message)
        signed_message = self.account.sign_message(message_encoded)

        return "0x" + signed_message.signature.hex()

    def sign_tx(self, tx: TxParams) -> SignedTransaction:
        return self.w3.eth.account.sign_transaction(tx, self.account.key)

    def send_tx(self, tx: TxParams, tx_label: str = "") -> str | bool:
        try:
            signed_tx = self.sign_tx(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            logger.info(f"{tx_label} | {self.chain.explorer}/tx/0x{tx_hash.hex()}")

            tx_receipt: TxReceipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=400)

            if tx_receipt["status"]:
                logger.success(f"{tx_label} | Tx confirmed \n")
                return "00x" + tx_hash.hex()

            raise Web3Exception(f"Tx Failed \n")

        except Web3RPCError as err:
            error_message = str(err).lower()

            if "insufficient funds" in error_message:
                logger.error(f"{tx_label} | Insufficient funds \n")
            elif "already known" in error_message:
                logger.warning(f"{tx_label} | Transaction already in mempool \n")
                return getattr(self, "tx_hash", True)
            else:
                logger.error(f"{tx_label} | RPC Error: {err} \n")

            return False

        except Web3Exception as err:
            logger.error(f"{tx_label} | Web3 Error: {err} \n")
            return False

    def transfer_token(self, token_address: str, amount: int | None = None) -> bool:
        if not self.recipient:
            return False

        token_contract = self.get_contract(token_address)
        token = self.get_token_info(token_address)

        transfer_amount = amount if amount else token["balance"]
        tx = token_contract.functions.transfer(self.recipient, transfer_amount).build_transaction(self.get_tx_params())

        return self.send_tx(
            tx,
            f"{self.label} Transfer {transfer_amount / 10**token['decimals']:.0f} {token['symbol']} to {self.recipient}",
        )
