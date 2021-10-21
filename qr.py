from PIL import Image

from constants import *
from encoding import *

def show_color(img, i, j, color):
    img.putpixel((i, j), color)

def is_free_pixel(img, i, j):
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

def show_finder_patterns(img, dim):
    show_finder_pattern(img, 0, 0, dim)
    show_finder_pattern(img, dim - 7, 0, dim)
    show_finder_pattern(img, 0, dim - 7, dim)

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

def show_alignment_patterns(img, version, dim):
    indices = alignments(version)
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
    for i in range(6):
        for j in range(3):
            bit = bits.pop(0)
            show_color(img, 5 - i, dim - 9 - j, bit_color(bit))
            show_color(img, dim - 9 - j, 5 - i, bit_color(bit))

def show_format(img, mode, mask, dim):
    data = encode_format(mode, mask)
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

def apply_mask(mask, i, j, bit):
    m = 1 if MASKS[mask](i, j) == 0 else 0
    return bit ^ m

def show_data(img, message, mode, enc, version, mask, dim):
    bits = encode_message(message, mode, enc, version)
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

                if is_free_pixel(img, i, j):
                    bit = 0
                    if len(bits) > 0:
                        bit = bits.pop(0)
                    bit = apply_mask(mask, i, j, bit)
                    show_color(img, i, j, bit_color(bit))

def make_qr_code(message, mode, mask, enc, version):
    if version is None:
        version = 1
        target = len(message)
        while capacity(version, mode, enc) < target and version < 41:
            version += 1
        if version > 40:
            raise ValueError("Message too long, " +
                "impossible to find a suitable version.")

    dim = dimension(version)
    img = Image.new(mode="RGB", size=(dim,dim), color=RED)

    # Finder patterns
    show_finder_patterns(img, dim)

    # Timer patterns
    show_timer_patterns(img, dim)

    # Black module
    show_color(img, 8, dim - 8, BLACK)

    # Alignment patterns
    show_alignment_patterns(img, version, dim)

    # Version
    show_version(img, version, dim)

    # Format
    show_format(img, mode, mask, dim)

    # Data
    show_data(img, message, mode, enc, version, mask, dim)

    return img
