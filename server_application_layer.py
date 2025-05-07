import json
import logging
from hamming_sed import decode_hamming_16_11, bits_to_string

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')

def parse_binary_chunks(sequence):
    if len(sequence) % 16 != 0:
        logging.error("Incoming bitstream length is not a multiple of 16.")
        raise ValueError("Incoming bitstream length is not a multiple of 16.")
    return [sequence[i:i + 16] for i in range(0, len(sequence), 16)]

def decode_bitstream(bitstream):
    logging.debug("Decoding bitstream...")

    decoded_bits = []
    blocks = parse_binary_chunks(bitstream) #this is a list of 16-bit long lists(blocks)

    for block in blocks:
        try:
            data_bits = decode_hamming_16_11(block)
            decoded_bits.extend(data_bits) #7ot decoded block fil decoded_bits list
        except ValueError:
            logging.error("Error during Hamming decoding: block is corrupted.")
            return {
                "operand1": None,
                "operand2": None,
                "operator": None,
                "result": "",
                "error": "Transmission error: data corrupted beyond correction."
            }

    # Extract original length from first 16 bits
    length_bits = decoded_bits[:16]
    original_length = int(''.join(map(str, length_bits)), 2)
    logging.debug(f"Original bitstream length (before padding): {original_length}")

    # Remove padding using original length
    json_bits = decoded_bits[16:16+original_length]
    from crypto_utils import decrypt_to_json_string

    # Convert trimmed bits to bytes
    byte_list = [int("".join(str(bit) for bit in json_bits[i:i + 8]), 2) for i in range(0, len(json_bits), 8)]
    cipher_data = bytes(byte_list)
    logging.debug("Bitstream converted to bytes. Decrypting...")

    try:
        json_string = decrypt_to_json_string(cipher_data)
        logging.debug(f"Decrypted JSON string: {json_string}")
    except Exception as e:
        logging.error(f"Decryption failed: {str(e)}")
        return {
            "operand1": None,
            "operand2": None,
            "operator": None,
            "result": "",
            "error": f"Decryption error: {str(e)}"
        }
    try:
        operation = json.loads(json_string) #json.loads() parses a JSON-formatted string and returns a corresponding Python object (e.g., dict, list)
    except json.JSONDecodeError:
        logging.error("Decoded JSON string is invalid.")
        return {
            "operand1": None,
            "operand2": None,
            "operator": None,
            "result": "",
            "error": "Decoded data is not valid JSON."
        }
    return perform_binary_operation(operation)

def perform_binary_operation(operation):
    a = operation.get("operand1")
    b = operation.get("operand2")
    op = operation.get("operator")
    logging.debug(f"Performing operation: {a} {op} {b}")
    try:
        a_int = int(a, 2)
        b_int = int(b, 2)
        if op == '+':
            res = a_int + b_int
        elif op == '-':
            res = a_int - b_int
        elif op == '*':
            res = a_int * b_int
        elif op == '/':
            if b_int == 0:
                raise ZeroDivisionError("Division by zero")
            res = a_int // b_int
        elif op == '&':
            res = a_int & b_int
        elif op == '|':
            res = a_int | b_int
        elif op == '^':
            res = a_int ^ b_int
        else:
            raise ValueError("Unsupported operator")
        operation["result"] = bin(res)[2:]
        operation["error"] = ""
        logging.info(f"Operation successful: result = {operation['result']}")

    except Exception as e:
        operation["result"] = ""
        operation["error"] = f"Computation error: {str(e)}"
        logging.error(f"Computation error: {str(e)}")
    return operation
