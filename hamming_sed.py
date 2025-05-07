
# === ENCODING FUNCTION ===
def encode_hamming_16_11(data_bits):
    """
    Takes a list of 11 bits and returns a 16-bit Hamming codeword (with SEC-DED).
    """
    if len(data_bits) != 11:
        raise ValueError("Data must be 11 bits long.")

    # Map the 11 data bits to their positions in the 16-bit codeword
    # Positions 1, 2, 4, 8, 16 (1-based) are reserved for parity bits (5 total)
    codeword = [0] * 16
    data_positions = [2, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14]  # 0-based index

    for i, pos in enumerate(data_positions):
        codeword[pos] = data_bits[i]

    # === Compute the 5 parity bits (using XOR logic on positions) ===
    # These positions are 1-based (for human clarity), so we adjust for 0-based Python indexing
    parity_positions = [0, 1, 3, 7, 15]  # parity bits: P1, P2, P4, P8, overall parity

    # Parity P1 (covers bits with 1 in bit 1 of position)
    codeword[0] = parity_bit(codeword, [0, 2, 4, 6, 8, 10, 12, 14])

    # Parity P2 (covers bits with 1 in bit 2)
    codeword[1] = parity_bit(codeword, [1, 2, 5, 6, 9, 10, 13, 14])

    # Parity P4
    codeword[3] = parity_bit(codeword, [3, 4, 5, 6, 11, 12, 13, 14])

    # Parity P8
    codeword[7] = parity_bit(codeword, [7, 8, 9, 10, 11, 12, 13, 14])

    # Overall parity (even parity for the whole codeword)
    codeword[15] = sum(codeword[:15]) % 2

    return codeword


# === DECODING FUNCTION ===
def decode_hamming_16_11(codeword):
    """
    Takes a 16-bit Hamming codeword and returns the corrected 11 data bits.
    Corrects 1-bit errors and detects 2-bit errors.
    """

    if len(codeword) != 16:
        raise ValueError("Codeword must be 16 bits long.")

    # Recompute parity checks (syndrome bits)
    s1 = parity_bit(codeword, [0, 2, 4, 6, 8, 10, 12, 14])
    s2 = parity_bit(codeword, [1, 2, 5, 6, 9, 10, 13, 14])
    s4 = parity_bit(codeword, [3, 4, 5, 6, 11, 12, 13, 14])
    s8 = parity_bit(codeword, [7, 8, 9, 10, 11, 12, 13, 14])
    overall_parity = sum(codeword[:15]) % 2
    expected_overall = codeword[15]

    # Syndrome = binary error position (1-based)
    syndrome = s1 * 1 + s2 * 2 + s4 * 4 + s8 * 8

    # SEC-DED logic
    if syndrome != 0:
        if overall_parity != codeword[15]:
            # Single-bit error: correct it
            error_pos = syndrome - 1  # Convert to 0-based
            if 0 <= error_pos < 16:
                codeword[error_pos] ^= 1  # Flip the erroneous bit
        else:
            # Detected a 2-bit error, cannot correct
            raise ValueError("Double-bit error detected and cannot be corrected.")

    # Extract 11 data bits
    data_positions = [2, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14]
    return [codeword[pos] for pos in data_positions]


# === Helper function to compute even parity ===
def parity_bit(bits, indices):
    return sum(bits[i] for i in indices) % 2


# === Convert bits to integer ===
def bits_to_int(bits):
    return int("".join(str(b) for b in bits), 2)

# === Convert 8-bit blocks to string ===
def bits_to_string(bits):
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        chars.append(chr(int("".join(str(b) for b in byte), 2)))
    return ''.join(chars)
