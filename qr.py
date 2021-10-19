from PIL import Image

from galois import *

def show_white(img, i, j):
    if i >= 0 and i < 21 and j >= 0 and j < 21:
        img.putpixel((i, j), 1)

def show_finder_pattern(img, i, j):
    for k in range(5):
        show_white(img, i + 1, j + 1 + k)
    for k in range(5):
        show_white(img, i + 5, j + 1 + k)
    for k in range(5):
        show_white(img, i + 1 + k, j + 1)
    for k in range(5):
        show_white(img, i + 1 + k, j + 5)
    for k in range(9):
        show_white(img, i - 1, j - 1 + k)
    for k in range(9):
        show_white(img, i + 7, j - 1 + k)
    for k in range(9):
        show_white(img, i - 1 + k, j - 1)
    for k in range(9):
        show_white(img, i - 1 + k, j + 7)

def show_format(img, data):
    for k in range(6):
        if data[k] == 0:
            show_white(img, k, 8)
    for k in range(2):
        if data[6 + k] == 0:
            show_white(img, 7 + k, 8)
    if data[8] == 0:
        show_white(img, 8, 7)
    for k in range(6):
        if data[9 + k] == 0:
            show_white(img, 8, 5 - k)

    for k in range(7):
        if data[k] == 0:
            show_white(img, 8, 20 - k)
    for k in range(8):
        if data[7 + k] == 0:
            show_white(img, 13 + k, 8)

MODE_M = 0
MODE_L = 1
MODE_H = 2
MODE_Q = 3

MODES_LENGTHS = [
    (16, 10),
    (19, 7),
    (9, 17),
    (13, 13),
]

def format(mode, mask):
    data = ((mode << 3) + mask) << 10
    extra = modulo(data, 0b10100110111)
    masked = (data + extra) ^ 0b101010000010010
    return to_bits(masked, 15)

MASKS = [
    lambda i, j: (i + j) % 2,
    lambda i, j: j % 2,
    lambda i, j: i % 3,
    lambda i, j: (i + j) % 3,
    lambda i, j: ((j // 2) + (i // 3)) % 2,
    lambda i, j: ((i * j) % 2) + ((i * j) % 3),
    lambda i, j: ((i * j) % 3 + i * j) % 2,
    lambda i, j: ((i * j) % 3 + i + j) % 2,
]

def apply_mask(mask, i, j, bit):
    m = 1 if MASKS[mask](i, j) == 0 else 0
    return bit ^ m

def up(i, j):
    return [(i + 1 - di, j + 3 - dj) for dj in range(4) for di in range(2)]

def up_special(i, j):
    high = [(i + 1 - di, j + 4 - dj) for dj in range(2) for di in range(2)]
    low = [(i + 1 - di, j + 1 - dj) for dj in range(2) for di in range(2)]
    return low + high

def down(i, j):
    return [(i + 1 - di, j + dj) for dj in range(4) for di in range(2)]

def down_special(i, j):
    high = [(i + 1 - di, j + dj) for dj in range(2) for di in range(2)]
    low = [(i + 1 - di, j + 3 + dj) for dj in range(2) for di in range(2)]
    return high + low

BITS_POSITIONS = [bit for bits in [
    up(19, 17),
    up(19, 13),
    up(19, 9),
    down(17, 9),
    down(17, 13),
    down(17, 17),
    up(15, 17),
    up(15, 13),
    up(15, 9),
    down(13, 9),
    down(13, 13),
    down(13, 17),
    up(11, 17),
    up(11, 13),
    up(11, 9),
    up_special(11, 4),
    up(11, 0),
    down(9, 0),
    down_special(9, 4),
    down(9, 9),
    down(9, 13),
    down(9, 17),
    up(7, 9),
    down(4, 9),
    up(2, 9),
    down(0, 9),
] for bit in bits]

def to_bits(byte, size=8):
    return [1 if byte & (1 << (size - 1 - i)) else 0 for i in range(size)]

def to_value(bits):
    r = 0
    for bit in bits:
        r = r << 1
        r = r + bit
    return r

def show_data(img, data, masque):
    assert(len(data) * 8 == len(BITS_POSITIONS))
    bits = [bit for byte in data for bit in to_bits(byte)]

    for (bit, position) in zip(bits, BITS_POSITIONS):
        (i, j) = position
        v = apply_mask(masque, i, j, bit)
        if v == 0:
            show_white(img, i, j)

ENC_NUMERIC = 0
ENC_ALPHANUMERIC = 1
ENC_BYTE = 2
ENC_KANJI = 3

ENC_CODE = [
    to_bits(1, 4),
    to_bits(2, 4),
    to_bits(4, 4),
    to_bits(8, 4),
    to_bits(7, 4),
]

ENC_LENGTH_BITS = [
    10,
    9,
    8,
    8,
]

def encode_numeric(message):
    for c in message:
        if c < '0' or c > '9':
            raise ValueError("Invalid!")

    bits = []
    while len(message) > 0:
        k = min(len(message), 3)
        partie = int(message[:k])
        message = message[k:]

        if k == 1:
            bits.extend(to_bits(partie, 4))
        elif k == 2:
            bits.extend(to_bits(partie, 7))
        else:
            bits.extend(to_bits(partie, 10))
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
        partie = message[:k]
        message = message[k:]

        if k == 2:
            a = encode_char(partie[0]) * 45
            b = encode_char(partie[1])
            bits.extend(to_bits(a + b, 11))
        else:
            a = encode_char(partie[0])
            bits.extend(to_bits(a, 6))
    return bits

def encode_bytes(message):
    try:
        bits = []
        for byte in message.encode("iso-8859-1"):
            bits.extend(to_bits(byte))
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
    to_bits(236),
    to_bits(17),
]

def encode_message(message, mode, enc):
    length = len(message)
    bits = []
    bits.extend(ENC_CODE[enc])
    bits.extend(to_bits(length, ENC_LENGTH_BITS[enc]))
    bits.extend(ENC_FONCTIONS[enc](message))

    (data_length, corr_length) = MODES_LENGTHS[mode]
    required = data_length * 8

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

    octets = []
    while len(bits) > 0:
        octets.append(to_value(bits[:8]))
        bits = bits[8:]

    encoder = Encoder(PolyRing(GaloisField()), corr_length)

    return encoder.encode(octets)

def make_qr_code(message, mode, mask, enc):
    img = Image.new(mode="1", size=(21,21))
    show_finder_pattern(img, 0, 0)
    show_finder_pattern(img, 14, 0)
    show_finder_pattern(img, 0, 14)
    show_white(img, 6, 9)
    show_white(img, 6, 11)
    show_white(img, 9, 6)
    show_white(img, 11, 6)
    show_format(img, format(mode, mask))
    data = encode_message(message, mode, enc)
    show_data(img, data, mask)
    return img
