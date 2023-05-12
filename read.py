from display import data_module_positions, apply_mask

def read_data(img, template, mask):
    """Read the data from the QR code img."""
    
    # Read all data modules of the image
    # based on the template and mask.
    positions = data_module_positions(template)
    bits = 0
    bits_len = 0
    while True:
        try:
            (x, y) = next(positions)
        except StopIteration:
            break
        p = img.getpixel((x, y))
        if not isinstance(p, int):
            p = p[0]
        bit = 1 if p <= 127 else 0
        bit = apply_mask(mask, x, y, bit)
        bits <<= 1
        bits_len += 1
        bits ^= bit

    extra = bits_len % 8
    if extra != 0:
        bits >>= extra
        bits_len -= extra
        
    # Convert the bits to bytes.
    bytes = []
    while bits_len >= 8:
        byte = bits & 0xFF
        bits >>= 8
        bits_len -= 8
        bytes.insert(0, byte)

    return bytes