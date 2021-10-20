from PIL import Image

from galois import *

RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def show_color(img, i, j, color):
    if i >= 0 and i < 21 and j >= 0 and j < 21:
        img.putpixel((i, j), color)

def free_pixel(img, i, j):
    return img.getpixel((i, j)) == RED

def bit_color(bit):
    if bit == 0:
        return WHITE
    else:
        return BLACK

def show_finder_pattern(img, i, j):
    for di in range(9):
        for dj in range(9):
            color = BLACK

            if di == 0 or di == 8:
                color = WHITE
            elif dj == 0 or dj == 8:
                color = WHITE
            elif (di == 2 or di == 6) and dj != 1 and dj != 7:
                color = WHITE
            elif (dj == 2 or dj == 6) and di != 1 and di != 7:
                color = WHITE

            show_color(img, i - 1 + di, j - 1 + dj, color)

def show_format(img, data):
    for k in range(6):
        show_color(img, k, 8, bit_color(data[k]))
    for k in range(2):
        show_color(img, 7 + k, 8, bit_color(data[6 + k]))
    show_color(img, 8, 7, bit_color(data[8]))
    for k in range(6):
        show_color(img, 8, 5 - k, bit_color(data[9 + k]))

    for k in range(7):
        show_color(img, 8, 20 - k, bit_color(data[k]))
    for k in range(8):
        show_color(img, 13 + k, 8, bit_color(data[7 + k]))

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

def show_data(img, data, mask):
    bits = []
    for byte in data:
        bits.extend(to_bits(byte, 8))

    for k in range(10):
        si = 20 - k * 2

        # Skip vertical timer pattern.
        if si <= 6:
            si = si - 1

        for j in range(21):
            if k % 2 == 0:
                # Up column
                j = 20 - j

            for di in range(2):
                i = si - di

                if free_pixel(img, i, j):
                    bit = apply_mask(mask, i, j, bits.pop(0))
                    show_color(img, i, j, bit_color(bit))


ENC_NUMERIC = 0
ENC_ALPHANUMERIC = 1
ENC_BYTE = 2
ENC_KANJI = 3

ENC_CODE = [
    to_bits(1, 4),
    to_bits(2, 4),
    to_bits(4, 4),
    to_bits(8, 4),
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
    img = Image.new(mode="RGB", size=(21,21), color=RED)
    show_finder_pattern(img, 0, 0)
    show_finder_pattern(img, 14, 0)
    show_finder_pattern(img, 0, 14)

    # Timer patterns
    show_color(img, 6, 8, BLACK)
    show_color(img, 6, 9, WHITE)
    show_color(img, 6, 10, BLACK)
    show_color(img, 6, 11, WHITE)
    show_color(img, 6, 12, BLACK)
    show_color(img, 8, 6, BLACK)
    show_color(img, 9, 6, WHITE)
    show_color(img, 10, 6, BLACK)
    show_color(img, 11, 6, WHITE)
    show_color(img, 12, 6, BLACK)

    # Black module
    show_color(img, 8, 13, BLACK)

    show_format(img, format(mode, mask))
    data = encode_message(message, mode, enc)
    show_data(img, data, mask)
    return img
