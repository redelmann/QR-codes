from constants import RED, WHITE, BLACK, alignments, MASKS

def bit(n, i):
    """Return the i-th bit of n, starting from the right."""

    return (n >> i) & 1

def show_color(img, i, j, color):
    """Display a color at coordinates (i, j)."""

    img.putpixel((i, j), color)

def is_free_pixel(img, i, j):
    """Return True if and only if the pixel at (i, j) is free."""
    return img.getpixel((i, j)) == RED

def bit_color(bit):
    """Return the color associated to a bit."""

    if bit == 0:
        return WHITE
    else:
        return BLACK

def apply_mask(mask, i, j, bit):
    """Apply a mask to a bit."""

    m = 1 if MASKS[mask](i, j) == 0 else 0
    return bit ^ m

def show_finder_pattern(img, i, j):
    """Display a finder pattern."""

    dim = img.width

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

def show_alignment_pattern(img, i, j):
    """Display an alignment pattern."""

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

def show_alignment_patterns(img, version):
    """Display the alignment patterns."""

    dim = img.width

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

def show_finder_patterns(img):
    """Display the finder patterns."""

    dim = img.width

    show_finder_pattern(img, 0, 0)
    show_finder_pattern(img, dim - 7, 0)
    show_finder_pattern(img, 0, dim - 7)

def show_timer_patterns(img):
    """Display the timer patterns."""
    dim = img.width
    i = 8
    while i < dim - 8:
        color = BLACK if i % 2 == 0 else WHITE
        show_color(img, 6, i, color)
        show_color(img, i, 6, color)
        i = i + 1

def show_format(img, encoded_format):
    """Display the format modules."""

    dim = img.width
    n = encoded_format

    # Place format information around the top-left corner.
    for k in range(6):
        show_color(img, k, 8, bit_color(bit(n, 14 - k)))
    for k in range(2):
        show_color(img, 7 + k, 8, bit_color(bit(n, 8 - k)))
    show_color(img, 8, 7, bit_color(bit(n, 6)))
    for k in range(6):
        show_color(img, 8, 5 - k, bit_color(bit(n, 5 - k)))

    # Place format information around the other corners.
    for k in range(7):
        show_color(img, 8, dim - 1 - k, bit_color(bit(n, 14 - k)))
    for k in range(8):
        show_color(img, dim - 8 + k, 8, bit_color(bit(n, 7 - k)))

def show_version(img, encoded_version):
    """Display the version information modules."""

    dim = img.width
    n = 17
    for i in range(6):
        for j in range(3):
            b = bit(encoded_version, n)
            n -= 1
            show_color(img, 5 - i, dim - 9 - j, bit_color(b))
            show_color(img, dim - 9 - j, 5 - i, bit_color(b))

def show_data(img, encoded_data, mask):
    """Display the data modules."""

    # Get a generator of positions.
    positions = data_module_positions(img)

    # Display the data modules.
    for byte in encoded_data:
        for i in range(8):
            b = bit(byte, 7 - i)
            (x, y) = next(positions)
            color = bit_color(apply_mask(mask, x, y, b))
            show_color(img, x, y, color)
    
    # Fill the rest with masked white modules.
    while True:
        try:
            (x, y) = next(positions)
        except StopIteration:
            break
        color = bit_color(apply_mask(mask, x, y, 0))
        show_color(img, x, y, color)

def data_module_positions(img):
    """Return a generator of positions of data modules."""

    dim = img.width

    # For all columns.
    for k in range((dim - 1) // 2):

        # Starting index of the column.
        si = dim - 1 - (k * 2)

        # Skip vertical timer pattern.
        if si <= 6:
            si = si - 1

        # For all rows.
        for j in range(dim):
            if k % 2 == 0:
                # Column is going up,
                # so we start from the bottom.
                j = dim - 1 - j

            # We place two modules every row.
            for di in range(2):
                i = si - di

                if is_free_pixel(img, i, j):
                    # Only yield free pixels.
                    yield (i, j)