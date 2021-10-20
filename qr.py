from PIL import Image

from galois import *

RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def show_color(img, i, j, color):
    img.putpixel((i, j), color)

def free_pixel(img, i, j):
    return img.getpixel((i, j)) == RED

def bit_color(bit):
    if bit == 0:
        return WHITE
    else:
        return BLACK

def show_finder_pattern(img, i, j, dim):
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

            ti = i - 1 + di
            tj = j - 1 + dj

            if ti >= 0 and ti < dim and tj >= 0 and tj < dim:
                show_color(img, i - 1 + di, j - 1 + dj, color)

def show_timer_patterns(img, dim):
    i = 8
    while i < dim - 8:
        color = BLACK if i % 2 == 0 else WHITE
        show_color(img, 6, i, color)
        show_color(img, i, 6, color)
        i = i + 1

def show_alignment_pattern(img, i, j):
    for di in range(-2, 3):
        for dj in range(-2, 3):
            color = WHITE
            if di == 0 and dj == 0:
                color = BLACK
            elif di == -2 or di == 2:
                color = BLACK
            elif dj == -2 or dj == 2:
                color = BLACK
            show_color(img, i + di, j + dj, color)

def alignments(version):
    return [
        [],    # Version 1
        [18],  # Version 2
        [22],  # Version 3
        [26],  # Version 4
        [30],  # Version 5
        [34],  # Version 6
        [6, 22, 38],  # Version 7
        [6, 24, 42],  # Version 8
        [6, 26, 46],  # Version 9
        [6, 28, 50],  # Version 10
        [6, 30, 54],  # Version 11
        [6, 32, 58],  # Version 12
        [6, 34, 62],  # Version 13
        [6, 26, 46, 66],  # Version 14
        [6, 26, 48, 70],  # Version 15
        [6, 26, 50, 74],  # Version 16
        [6, 30, 54, 78],  # Version 17
        [6, 30, 56, 82],  # Version 18
        [6, 30, 58, 86],  # Version 19
        [6, 34, 62, 90],  # Version 20
        [6, 28, 50, 72, 94],  # Version 21
    ][version - 1]

def show_alignment_patterns(img, indices, dim):
    for i in indices:
        for j in indices:
            if (i == 6 and j == 6):
                continue
            if (i == 6 and j == dim - 7):
                continue
            if (i == dim - 7 and j == 6):
                continue
            show_alignment_pattern(img, i, j)

def show_version(img, version, dim):
    if version < 7:
        return

    bits = encode_version(version)
    for i in reversed(range(6)):
        for j in reversed(range(3)):
            bit = bits.pop(0)
            show_color(img, i, dim - 11 + j, bit_color(bit))
            show_color(img, dim - 11 + j, i, bit_color(bit))


def show_format(img, data, dim):
    for k in range(6):
        show_color(img, k, 8, bit_color(data[k]))
    for k in range(2):
        show_color(img, 7 + k, 8, bit_color(data[6 + k]))
    show_color(img, 8, 7, bit_color(data[8]))
    for k in range(6):
        show_color(img, 8, 5 - k, bit_color(data[9 + k]))

    for k in range(7):
        show_color(img, 8, dim - 1 - k, bit_color(data[k]))
    for k in range(8):
        show_color(img, dim - 8 + k, 8, bit_color(data[7 + k]))

MODE_M = 0
MODE_L = 1
MODE_H = 2
MODE_Q = 3

MODE_LENGTHS = [
    [   # Version 1
        ([16], 10),
        ([19], 7),
        ([9], 17),
        ([13], 13),
    ],
    [   # Version 2
        ([28], 16),
        ([34], 10),
        ([16], 28),
        ([22], 22),
    ],
    [   # Version 3
        ([44], 26),
        ([55], 15),
        ([13] * 2, 22),
        ([17] * 2, 18),
    ],
    [   # Version 4
        ([32] * 2, 18),
        ([80], 20),
        ([9] * 4, 16),
        ([24] * 2, 26),
    ],
    [   # Version 5
        ([43] * 2, 24),
        ([108], 26),
        ([11] * 2 + [12] * 2, 22),
        ([15] * 2 + [16] * 2, 18),
    ],
    [   # Version 6
        ([27] * 4, 16),
        ([68] * 2, 18),
        ([15] * 4, 28),
        ([19] * 4, 24),
    ],
    [   # Version 7
        ([31] * 4, 18),
        ([78] * 2, 20),
        ([13] * 4 + [14], 26),
        ([14] * 2 + [15] * 4, 18),
    ],
    [   # Version 8
        ([38] * 2 + [39] * 2, 22),
        ([97] * 2, 24),
        ([14] * 4 + [15] * 2, 26),
        ([18] * 4 + [19] * 2, 22),
    ],
    [   # Version 9
        ([36] * 3 + [37] * 2, 22),
        ([116] * 2, 30),
        ([12] * 4 + [13] * 4, 24),
        ([16] * 4 + [17] * 4, 20),
    ],
    [   # Version 10
        ([43] * 4 + [44], 26),
        ([68] * 2 + [69] * 2, 18),
        ([15] * 6 + [16] * 2, 28),
        ([19] * 6 + [20] * 2, 24),
    ],
    [   # Version 11
        ([50] + [51] * 4, 30),
        ([81] * 4, 20),
        ([12] * 3 + [13] * 8, 24),
        ([22] * 4 + [23] * 4, 28),
    ],
    [   # Version 12
        ([36] * 6 + [37] * 2, 22),
        ([92] * 2 + [93] * 2, 24),
        ([14] * 7 + [15] * 4, 28),
        ([20] * 4 + [21] * 6, 26),
    ],
    [   # Version 13
        ([37] * 8 + [38], 22),
        ([107] * 4, 26),
        ([11] * 12 + [12] * 4, 22),
        ([20] * 8 + [21] * 4, 24),
    ],
    [   # Version 14
        ([40] * 4 + [41] * 5, 24),
        ([115] * 3 + [116], 30),
        ([12] * 11 + [13] * 5, 24),
        ([16] * 11 + [17] * 5, 20),
    ],
    [   # Version 15
        ([41] * 5 + [42] * 5, 24),
        ([87] * 5 + [88], 22),
        ([12] * 11 + [13] * 7, 24),
        ([24] * 5 + [25] * 7, 30),
    ],
    [   # Version 16
        ([45] * 7 + [46] * 3, 28),
        ([98] * 5 + [99], 24),
        ([15] * 3 + [16] * 13, 30),
        ([19] * 15 + [20] * 2, 24),
    ],
    [   # Version 17
        ([46] * 10 + [47], 28),
        ([107] + [108] * 5, 28),
        ([14] * 2 + [15] * 17, 28),
        ([22] + [23] * 15, 28),
    ],
    [   # Version 18
        ([43] * 9 + [44] * 4, 26),
        ([120] * 5 + [121], 30),
        ([14] * 2 + [15] * 19, 28),
        ([22] * 17 + [23], 28),
    ],
    [   # Version 19
        ([44] * 3 + [45] * 11, 26),
        ([113] * 3 + [114] * 4, 28),
        ([13] * 9 + [14] * 16, 26),
        ([21] * 17 + [22] * 4, 26),
    ],
    [   # Version 20
        ([41] * 3 + [42] * 13, 26),
        ([107] * 3 + [108] * 5, 28),
        ([15] * 15 + [16] * 10, 28),
        ([24] * 15 + [25] * 5, 30),
    ],
    [   # Version 21
        ([42] * 17, 26),
        ([116] * 4 + [117] * 4, 28),
        ([16] * 19 + [17] * 6, 30),
        ([22] * 17 + [23] * 6, 28),
    ],
]

def mode_lengths(mode, version):
    return MODE_LENGTHS[version - 1][mode]

def encode_format(mode, mask):
    data = ((mode << 3) + mask) << 10
    extra = modulo(data, 0b10100110111)
    masked = (data + extra) ^ 0b101010000010010
    return to_bits(masked, 15)

def encode_version(version):
    data = version << 12
    extra = modulo(data, 0b1111100100101)
    return to_bits(data + extra, 18)

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

def show_data(img, data, mask, dim):
    bits = []
    for byte in data:
        bits.extend(to_bits(byte, 8))

    for k in range((dim - 1) // 2):
        si = dim - 1 - (k * 2)

        # Skip vertical timer pattern.
        if si <= 6:
            si = si - 1

        for j in range(dim):
            if k % 2 == 0:
                # Up column
                j = dim - 1 - j

            for di in range(2):
                i = si - di

                if free_pixel(img, i, j):
                    bit = 0
                    if len(bits) > 0:
                        bit = bits.pop(0)
                    bit = apply_mask(mask, i, j, bit)
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

def enc_length_bits(version, enc):
    if version < 10:
        lengths = [
            10,
            9,
            8,
            8,
        ]
    elif version < 27:
        lengths = [
            12,
            11,
            16,
            10,
        ]
    else:
        lengths = [
            14,
            13,
            16,
            12,
        ]

    return lengths[enc]

def dimension(version):
    return 17 + 4 * version

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

    encoder = Encoder(PolyRing(GaloisField()), corr_length)

    data_blocks = []
    corr_blocks = []
    for data_length in data_lengths:
        bs = []
        for i in range(data_length):
            bs.append(to_value(bits[:8]))
            bits = bits[8:]
        data_blocks.append(bs)
        corr_blocks.append(encoder.encode(bs))

    out = []
    for _ in range(max(data_lengths)):
        for block in data_blocks:
            if len(block) > 0:
                out.append(block.pop(0))

    for _ in range(corr_length):
        for block in corr_blocks:
            out.append(block.pop(0))

    return out

def make_qr_code(message, mode, mask, enc, version):
    dim = dimension(version)

    img = Image.new(mode="RGB", size=(dim,dim), color=RED)

    # Finder patterns
    show_finder_pattern(img, 0, 0, dim)
    show_finder_pattern(img, dim - 7, 0, dim)
    show_finder_pattern(img, 0, dim - 7, dim)

    # Timer patterns
    show_timer_patterns(img, dim)

    # Black module
    show_color(img, 8, dim - 8, BLACK)

    # Alignment patterns
    show_alignment_patterns(img, alignments(version), dim)

    # Version
    show_version(img, version, dim)

    # Format
    show_format(img, encode_format(mode, mask), dim)
    data = encode_message(message, mode, enc, version)
    show_data(img, data, mask, dim)
    return img
