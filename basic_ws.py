import json
import logging
import socket

import example_utils
from hyperliquid.utils import constants

C_HOST = 'localhost'
C_PORT = 8686


class LP:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((C_HOST, C_PORT))
        self.address, self.info, _ = example_utils.setup(constants.MAINNET_API_URL)

    def subscribe(self, coin):
        self.info.subscribe({"type": "l2Book", "coin": coin}, self.save_result)

    def save_result(self, response: str):
        msg = json.dumps(response) + chr(10)
        self.socket.send(msg.encode())


def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        filename='hyperliquid.log',
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


if __name__ == "__main__":
    setup_logging()
    lp = LP()
    lp.subscribe(coin="ETH")
    lp.subscribe(coin="BTC")
    lp.subscribe(coin="SOL")
