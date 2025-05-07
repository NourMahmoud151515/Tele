
import socket
import logging
import json
from server_application_layer import decode_bitstream

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(asctime)s - %(message)s',
)
HOST = 'localhost'
PORT = 5000
def start_server():
    logging.info(f"Server listening on {HOST}:{PORT}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        logging.debug("Server is now listening...")

        while True:
            logging.debug("Waiting for a new connection...")
            conn, addr = s.accept()
            with conn:
                logging.info(f"Connected by {addr}")

                # Receive data
                data = conn.recv(10000)
                if not data:
                    logging.warning("No data received.")
                    continue  # Go back to wait for another client

                logging.debug(f"Raw data received: {data[:60]}... (truncated)")
                bitstream = list(map(int, data.decode()))

                logging.info(f"Received bitstream ({len(bitstream)} bits).")
                result = decode_bitstream(bitstream)

                # Send result back
                response_str = str(result)
                conn.sendall(response_str.encode())
                logging.info("Result sent back to client.")

if __name__ == '__main__':
    start_server()
