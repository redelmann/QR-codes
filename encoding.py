from constants import *
from galois import *

def encode_format(mode, mask):
    """Encode the format."""

    data = ((mode << 3) + mask) << 10
    extra = modulo(data, 0b10100110111)
    return data ^ extra ^ 0b101010000010010

def encode_version(version):
    """Encode the version."""

    data = version << 12
    extra = modulo(data, 0b1111100100101)
    return data ^ extra

def encode_numeric(message):
    for c in message:
        if c < '0' or c > '9':
            raise ValueError("Invalid!")

    bits = 0
    bits_len = 0
    while len(message) > 0:
        k = min(len(message), 3)
        part = int(message[:k])
        message = message[k:]

        if k == 1:
            bits <<= 4
            bits_len += 4
        elif k == 2:
            bits <<= 7
            bits_len += 7
        else:
            bits <<= 10
            bits_len += 10
        bits ^= part
    return bits, bits_len

def encode_alphanumeric(message):
    specials = " $%*+-./:"

    def encode_char(c):
        if c >= '0' and c <= '9':
            return ord(c) - ord('0')
        if c >= 'A' and c <= 'Z':
            return ord(c) - ord('A') + 10
        if c in specials:
            return specials.index(c) + 36
        raise ValueError("Invalid!")

    bits = 0
    bits_len = 0
    while len(message) > 0:
        k = min(len(message), 2)
        part = message[:k]
        message = message[k:]

        if k == 2:
            a = encode_char(part[0]) * 45
            b = encode_char(part[1])
            bits <<= 11
            bits ^= a + b
            bits_len += 11
        else:
            a = encode_char(part[0])
            bits <<= 6
            bits ^= a
            bits_len += 6
    return bits, bits_len

def encode_bytes(message):
    bits = 0
    bits_len = 0
    for byte in message.encode("iso-8859-1"):
        bits <<= 8
        bits ^= byte
        bits_len += 8
    return bits, bits_len

def encode_kanji(message):
    bits = 0
    bits_len = 0
    bytes = message.encode("shift-jis")
    
    if len(bytes) % 2 == 1:
        raise ValueError("Invalid!")

    while len(bytes) > 0:

        a = bytes[0] << 8
        b = bytes[1]
        double_byte = a ^ b
        bytes = bytes[2:]

        if double_byte >= 0x8140 and double_byte <= 0x9FFC:
            double_byte -= 0x8140
        elif double_byte >= 0xE040 and double_byte <= 0xEBBF:
            double_byte -= 0xC140
        else:
            raise ValueError("Invalid!")

        a = double_byte >> 8
        b = double_byte & ((2 ** 8) - 1)
        bits <<= 13
        bits ^= a * 0xC0 + b
        bits_len += 13
    return bits, bits_len

ENC_FONCTIONS = [
    encode_numeric,
    encode_alphanumeric,
    encode_bytes,
    encode_kanji,
]

PAD_BITS = [
    236,
    17,
]

def encode_message(message, mode, enc, version, pads=None):
    """Encode the message."""

    bits = 0
    bits_len = 0

    # Encoding indicator.
    bits <<= 4
    bits_len += 4
    bits ^= ENC_CODE[enc]

    # Length indicator.
    enc_length = enc_length_bits(version, enc)
    bits <<= enc_length
    bits_len += enc_length
    bits ^= len(message)

    # Message bits.
    bits_message, bits_message_len = \
        ENC_FONCTIONS[enc](message)
    bits <<= bits_message_len
    bits_len += bits_message_len
    bits ^= bits_message
    
    (data_lengths, corr_length) = mode_lengths(mode, version)
    
    # Check if the message not too long enough.
    required = sum(data_lengths) * 8
    if bits_len > required:
        raise ValueError("Message too long!")

    # Pad the message with at most four 0.
    pad_number = min(4, required - bits_len)
    bits <<= pad_number    
    bits_len += pad_number

    # Pad the message with zero until
    # the message length is a multiple of 8.
    extra = bits_len % 8
    if extra > 0:
        bits <<= (8 - extra)
        bits_len += (8 - extra)

    start_pads = bits_len // 8

    # Pad the message with extra bytes.
    if pads is None:
        # Pad the message according to the standard.
        i = 0
        while bits_len != required:
            bits <<= 8
            bits_len += 8
            bits ^= PAD_BITS[i]
            i = (i + 1) % 2
    else:
        # Pad the message according to target bytes.

        # Creates a mapping from the octet position to the
        # padding octet.
        pad_map = [0] * (required // 8)
        i = 0
        ixs = []
        for data_length in data_lengths:
            ixs.append(list(range(i, data_length + i)))
            i += data_length
        i = 0
        for _ in range(max(data_lengths)):
            for l in ixs:
                if len(l) > 0:
                    pad_map[l.pop(0)] = i
                    i += 1

        # Pad the message.
        i = 0
        while bits_len != required:
            n = pad_map[start_pads + i]
            bits <<= 8
            bits_len += 8
            bits ^= pads[n]
            i = i + 1

    # Add error correction modules.
    encoder = Encoder(corr_length, 0b100011101)

    # Split the data into blocks and
    # add error correction bytes.
    data_blocks = []
    corr_blocks = []
    for data_length in reversed(data_lengths):
        # Reverse order as we start from the end of bits.
        bytes = []
        for i in range(data_length):
            bytes.insert(0, bits & 0xFF)
            bits >>= 8
            bits_len -= 8
        data_blocks.insert(0, bytes)
        corr_blocks.insert(0, encoder.encode(bytes))

    out_bytes = []
    for _ in range(max(data_lengths)):
        for block in data_blocks:
            if len(block) > 0:
                out_bytes.append(block.pop(0))

    for _ in range(corr_length):
        for block in corr_blocks:
            out_bytes.append(block.pop(0))
    
    return out_bytes