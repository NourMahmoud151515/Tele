import socket
import json
from client_application_layer import prepare_message, get_user_input
HOST = 'localhost'
PORT = 5000
def run_client():
    op1, op2, operator = get_user_input()
    bitstream = prepare_message(op1, op2, operator)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # Send the bitstream as a string of 0s and 1s
        bit_string = ''.join(str(bit) for bit in bitstream)
        s.sendall(bit_string.encode())

        print("Bitstream sent to server.")

        # Receive result
        response = s.recv(4096).decode()
        print("\n--- Server Response ---")
        print(response)

if __name__ == '__main__':
    run_client()


