import json
import socket

import websocket
import threading
import time

C_HOST = 'localhost'
C_PORT = 8687


class BinanceOrderBookWebSocket:
    def __init__(self, symbols, contract_type='quarterly', update_speed='100ms'):
        """
        Initialize Binance WebSocket connection for order book

        Parameters:
        symbol (str): Trading pair symbol (e.g., 'btcusdt')
        update_speed (str): Update frequency, options: '100ms' or '1000ms'
        """
        self.symbols = [s.lower() for s in symbols]
        self.update_speed = update_speed
        self.contract_type = contract_type
        self.ws = None
        self.last_update_id = 0
        self.ws_thread = None
        self.is_connected = False
        self.is_running = False

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((C_HOST, C_PORT))

    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        data = message + chr(10)
        self.socket.send(data.encode())

        print(message)

    def _on_error(self, ws, error):
        """Handle WebSocket errors"""
        print(f"Error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection close"""
        print(f"WebSocket closed: {close_status_code} - {close_msg}")
        self.is_connected = False

    def _on_open(self, ws):
        """Handle WebSocket connection open"""
        print(f"WebSocket connection opened for {self.symbols} order book")
        self.is_connected = True

    def _get_websocket_url(self):
        if self.contract_type == 'perpetual':
            # (USDT-M)
            return "wss://fstream.binance.com/stream"
        elif self.contract_type == 'quarterly':
            # (COIN-M)
            return "wss://dstream.binance.com/stream"
        else:
            raise ValueError(f"Unknow contract type: {self.contract_type}")

    def start(self):

        streams = [f"{symbol}@depth@{self.update_speed}" for symbol in self.symbols]

        # Получаем URL для фьючерсного WebSocket
        base_url = self._get_websocket_url()

        # Binance WebSocket endpoint for order book

        combined_stream_url = f"{base_url}?streams={'/'.join(streams)}"

        # Create WebSocket connection
        self.ws = websocket.WebSocketApp(
            combined_stream_url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )

        # Start WebSocket in a separate thread
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True  # Thread will exit when main program exits
        self.ws_thread.start()
        self.is_running = True

        # Wait for connection to establish
        timeout = 30  # seconds
        start_time = time.time()
        while not self.is_connected and time.time() - start_time < timeout:
            time.sleep(0.1)

        if not self.is_connected:
            print("Failed to establish WebSocket connection")
            return False

        return True

    def stop(self):
        """Stop WebSocket connection"""
        if self.ws and self.is_running:
            self.ws.close()
            self.is_running = False
            print("WebSocket connection closed")


if __name__ == "__main__":
    # Configuration
    symbols = ["btcusdc", "ethusdc"]  # Trading pair
    update_speed = "100ms"  # Options: "100ms" or "1000ms"

    try:
        # Enable debug output for WebSocket
        # websocket.enableTrace(True)

        # Create and start order book WebSocket
        order_book_ws = BinanceOrderBookWebSocket(symbols, 'perpetual', update_speed)
        if order_book_ws.start():
            print(f"Successfully connected to {symbols} order book stream")

            while True:
                pass
    except Exception as e:
        print(f"An error occurred: {e}")
