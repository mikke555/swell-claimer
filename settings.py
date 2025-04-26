########################################################################
#                           General Settings                           #
########################################################################

RPC_LIST = {
    "ethereum": "https://eth.drpc.org",
    "arbitrum": "https://arbitrum.meowrpc.com",
    "base": "https://mainnet.base.org",
    "optimism": "https://mainnet.optimism.io",
    "linea": "https://rpc.linea.build",
    "swell": "https://swell-mainnet.alt.technology",
}

USE_PROXY = False
SHUFFLE_KEYS = False

SLEEP_BETWEEN_WALLETS = [10, 20]
SLEEP_BETWEEN_ACTIONS = [10, 20]

TRUNCATE_ADDRESS_IN_LOGS = False


########################################################################
#                           Action Settings                            #
########################################################################

SEND_TO_EXCHANGE = True

REFUEL_SETTINGS = {
    "min_balance": 0.000055,
    "chains": ["optimism", "base", "arbitrum", "linea"],
    "refuel_amount": [0.00005, 0.0001],
}
