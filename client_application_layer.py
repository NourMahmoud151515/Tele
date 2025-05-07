import json
import random
from hamming_sed import encode_hamming_16_11

#CONFIGURATION
BIT_ERROR_RATE = 0.001  # to simulate noise

#Utility Functions
def string_to_bits(s):
    return [int(b) for char in s for b in format(ord(char), '08b')]

def bits_to_blocks(bits, block_size=11):
    padded = bits[:] #[:] means “take everything”
    while len(padded) % block_size != 0:
        padded.append(0) #padding to make the number of bits a multiple of 11
    return [padded[i:i+block_size] for i in range(0, len(padded), block_size)] #This chops the padded list into chunks of 11 bits.It returns a list of those chunks.

def introduce_errors(bits, error_rate):
    noisy_bits = bits[:]
    for i in range(len(noisy_bits)): #random.random() uses a uniform distribution over the range [0.0, 1.0)
        if random.random() < error_rate:
            noisy_bits[i] ^= 1
    return noisy_bits

def prepare_message(op1, op2, operator):
    data = {
        "operand1": op1,
        "operand2": op2,
        "operator": operator,
        "result": "",
        "error": ""
    }

    json_str = json.dumps(data) #json.dumps(data) converts a Python object (like a dict or list) into a JSON-formatted string.
    from crypto_utils import encrypt_json_string
    encrypted_bytes = encrypt_json_string(json_str)
    bitstream = [int(b) for byte in encrypted_bytes for b in format(byte, '08b')]

    original_length = len(bitstream)

    # Encode original length in 16 bits and prepend to bitstream
    length_bits = [int(b) for b in format(original_length, '016b')]
    full_bitstream = length_bits + bitstream

    blocks = bits_to_blocks(full_bitstream)

    codeword_bits = []
    for block in blocks:
        encoded = encode_hamming_16_11(block)
        noisy_encoded = introduce_errors(encoded, BIT_ERROR_RATE)
        codeword_bits.extend(noisy_encoded)

    return codeword_bits


def get_user_input():
    print("Binary Calculator Client")
    print("Please enter the operation as a list: ['operator', operand1, operand2, '∅']")
    user_input = input("Enter operation: ")
    try:
        # Safely evaluate the string input into a Python list
        operation = eval(user_input)
        if not isinstance(operation, list) or len(operation) != 4:
            raise ValueError("Input must be a list with 4 elements.")
        operator, op1, op2, result = operation
        valid_operators = ['+', '-', '*', '/', '&', '|', '^']
        # Check if operator is valid
        if operator not in valid_operators:
            raise ValueError("Invalid operator.")
        # Convert operands to string and validate binary
        op1 = str(op1)
        op2 = str(op2)
        if not all(c in '01' for c in op1) or not all(c in '01' for c in op2):
            raise ValueError("Operands must be binary (only 0s and 1s).")
        return op1, op2, operator
    except Exception as e:
        print(f"Input error: {e}")
        return None, None, None
