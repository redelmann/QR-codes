from PIL import Image

from constants import *
from encoding import *
from display import *

def make_qr_template(mode, mask, version):
    dim = dimension(version)
    img = Image.new(mode="RGBA", size=(dim,dim), color=RED)

    # Finder patterns
    show_finder_patterns(img)

    # Timer patterns
    show_timer_patterns(img)

    # Black module
    show_color(img, 8, dim - 8, BLACK)

    # Alignment patterns
    show_alignment_patterns(img, version)

    # Version
    if version >= 7:
        encoded_version = encode_version(version)
        show_version(img, encoded_version)

    # Format
    encoded_format = encode_format(mode, mask)
    show_format(img, encoded_format)

    return img

def make_qr_code(message, mode, mask, enc, version, pads=None):
    if version is None:
        version = 1
        target = len(message)
        while version < MAX_VERSION and capacity(version, mode, enc) < target:
            version += 1
        if capacity(version, mode, enc) < target:
            raise ValueError("Message too long, " +
                "impossible to find a suitable version.")

    # Place all modules that are not related
    # directly to the message.
    img = make_qr_template(mode, mask, version)

    # Place all modules of the message.
    encoded_message = encode_message(message, mode, enc, version, pads)
    show_data(img, encoded_message, mask)

    return img
