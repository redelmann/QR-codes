from constants import *
from galois import *

def to_bits(byte, size):
    bits = []
    for i in range(size):
        bits.append((byte >> ((size - 1) - i)) & 1)
    return bits

def to_value(bits):
    r = 0
    for bit in bits:
        r = r << 1
        r = r + bit
    return r

def encode_format(mode, mask):
    data = ((mode << 3) + mask) << 10
    extra = modulo(data, 0b10100110111)
    masked = (data + extra) ^ 0b101010000010010
    return to_bits(masked, 15)

def encode_version(version):
    data = version << 12
    extra = modulo(data, 0b1111100100101)
    return to_bits(data + extra, 18)

def encode_numeric(message):
    for c in message:
        if c < '0' or c > '9':
            raise ValueError("Invalid!")

    bits = []
    while len(message) > 0:
        k = min(len(message), 3)
        part = int(message[:k])
        message = message[k:]

        if k == 1:
            bits.extend(to_bits(part, 4))
        elif k == 2:
            bits.extend(to_bits(part, 7))
        else:
            bits.extend(to_bits(part, 10))
    return bits

def encode_alphanumeric(message):
    speciaux = " $%*+-./:"

    def encode_char(c):
        if c >= '0' and c <= '9':
            return ord(c) - ord('0')
        if c >= 'A' and c <= 'Z':
            return ord(c) - ord('A') + 10
        if c in speciaux:
            return speciaux.index(c) + 36
        raise ValueError("Invalid!")

    bits = []
    while len(message) > 0:
        k = min(len(message), 2)
        part = message[:k]
        message = message[k:]

        if k == 2:
            a = encode_char(part[0]) * 45
            b = encode_char(part[1])
            bits.extend(to_bits(a + b, 11))
        else:
            a = encode_char(part[0])
            bits.extend(to_bits(a, 6))
    return bits

def encode_bytes(message):
    try:
        bits = []
        for byte in message.encode("iso-8859-1"):
            bits.extend(to_bits(byte, 8))
        return bits
    except:
        raise ValueError("Invalid!") from None

def encode_kanji(message):
    bits = []
    bs = message.encode("shift-jis")
    while len(bs) > 0:
        k = min(len(bs), 2)
        parts = bs[:k]
        bs = bs[k:]

        if k == 2:
            a = parts[0] << 8
            b = parts[1]
            double_byte = a + b

            if double_byte >= 0x8140 and double_byte <= 0x9FFC:
                double_byte -= 0x8140
            elif double_byte >= 0xE040 and double_byte <= 0xEBBF:
                double_byte -= 0xC140
            else:
                raise ValueError("Invalid!")

            a = double_byte >> 8
            b = double_byte & ((2 ** 8) - 1)
            bits.extend(to_bits(a * 0xC0 + b, 13))
        else:
            raise ValueError("Invalid!")
    return bits

ENC_FONCTIONS = [
    encode_numeric,
    encode_alphanumeric,
    encode_bytes,
    encode_kanji,
]

PAD_BITS = [
    to_bits(236, 8),
    to_bits(17, 8),
]

def encode_message(message, mode, enc, version):
    length = len(message)
    bits = []
    bits.extend(ENC_CODE[enc])
    bits.extend(to_bits(length, enc_length_bits(version, enc)))
    bits.extend(ENC_FONCTIONS[enc](message))

    (data_lengths, corr_length) = mode_lengths(mode, version)
    required = sum(data_lengths) * 8

    if len(bits) > required:
        raise ValueError("Message too long!")

    pad_number = min(4, required - len(bits))
    bits.extend([0] * pad_number)

    extra = len(bits) % 8
    if extra > 0:
        bits.extend([0] * (8 - extra))

    i = 0
    while len(bits) != required:
        bits.extend(PAD_BITS[i])
        i = (i + 1) % 2

    encoder = Encoder(corr_length, 0b100011101)

    data_blocks = []
    corr_blocks = []
    for data_length in data_lengths:
        bs = []
        for i in range(data_length):
            bs.append(to_value(bits[:8]))
            bits = bits[8:]
        data_blocks.append(bs)
        corr_blocks.append(encoder.encode(bs))

    out_bytes = []
    for _ in range(max(data_lengths)):
        for block in data_blocks:
            if len(block) > 0:
                out_bytes.append(block.pop(0))

    for _ in range(corr_length):
        for block in corr_blocks:
            out_bytes.append(block.pop(0))

    out_bits = []
    for byte in out_bytes:
        out_bits.extend(to_bits(byte, 8))

    return out_bits