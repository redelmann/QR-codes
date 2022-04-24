import argparse
import sys

from qr import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='QR codes generator.')
    parser.add_argument('string',
        type=str,
        nargs='?',
        help='contents of the QR code')
    parser.add_argument('--mask',
        metavar='K',
        type=int,
        const=1,
        default=1,
        nargs='?',
        choices=range(8),
        help='data mask')
    parser.add_argument('--mode',
        metavar='M',
        type=str,
        const='L',
        default='L',
        nargs='?',
        choices="LMQH",
        help='error correction mode')
    parser.add_argument('--enc',
        metavar='E',
        type=str,
        const='byte',
        default='byte',
        nargs='?',
        choices=['byte', 'alpha', 'num', 'kanji'],
        help='encoding mode')
    parser.add_argument('--file',
        metavar='F',
        type=str,
        const=None,
        default=None,
        nargs='?',
        help='output file')
    parser.add_argument('--scale',
        metavar='S',
        type=int,
        const=10,
        default=10,
        nargs='?',
        help='scale factor')
    parser.add_argument('--version',
        metavar='V',
        type=int,
        const=None,
        default=None,
        nargs='?',
        help='QR version')
    parser.add_argument('--logo',
        metavar='F',
        type=str,
        const=None,
        default=None,
        nargs='?',
        help='logo file')
    parser.add_argument('--logoscale',
        metavar='S',
        type=int,
        const=1,
        default=1,
        nargs='?',
        help='logo scale factor')
    parser.add_argument('--margin',
        metavar='M',
        type=int,
        const=0,
        default=0,
        nargs='?',
        help='margin around the QR code, i.e. quiet zone')
    parser.add_argument('--target',
        metavar='F',
        type=str,
        const=None,
        default=None,
        nargs='?',
        help='target file')

    args = parser.parse_args()

    # Encoding for the message.
    enc = {
        'byte': ENC_BYTE,
        'alpha': ENC_ALPHANUMERIC,
        'num': ENC_NUMERIC,
        'kanji': ENC_KANJI,
    }[args.enc]

    # Error correction level.
    mode = {
        'L': MODE_L,
        'M': MODE_M,
        'Q': MODE_Q,
        'H': MODE_H,
    }[args.mode]

    # Read the message.
    message = args.string
    if message is None:
        message = sys.stdin.read()

    # Version number.
    version = args.version

    # Mask.
    mask = args.mask

    # Determine desired padding bytes, if any.
    # This is done so that we can display images
    # within the QR code by abusing the padding.
    if args.target is None:
        pads = None
    else:
        # Read the image.
        target_img = Image.open(args.target)

        # Ensure the image is square.
        if target_img.width != target_img.height:
            raise ValueError("Target image not square.")

        # Ensure the image has size compatible with a QR code.
        n = target_img.width - 17
        if n % 4 != 0:
            raise ValueError("Target image not of correct dimension.")

        # Find the QR version given the dimensions.
        target_version = n // 4
        if not (1 <= target_version <= MAX_VERSION):
            raise ValueError("Target image not of correct dimension.")

        # Ensure that specified version (if any) and target version match.
        if version is not None and target_version != version:
            raise ValueError("Target image not of correct dimension.")
        
        # Use the target version.
        version = target_version
        
        # Create a template QR code (without data modules)
        # to be able to determine the position of the data modules.
        template_img = make_qr_template(mode, mask, version)

        # Read the target bytes.
        import read
        pads = read.read_data(target_img, template_img, mask)
    
    # Create the QR code.
    img = make_qr_code(message, mode, mask, enc, version, pads)

    # Scale the size of QR code.
    if args.scale > 1:
        width, height = img.size
        img = img.resize((args.scale * width, args.scale * height), resample=Image.BOX)

    # Add a logo in the center.
    if args.logo is not None:
        logo = Image.open(args.logo)
        img_width, img_height = img.size
        logo_width, logo_height = logo.size

        if args.logoscale > 1:
            logo_width = logo_width * args.logoscale
            logo_height = logo_height * args.logoscale
            logo = logo.resize((logo_width, logo_height), resample=Image.BOX)

        x = (img_width - logo_width) // 2
        y = (img_height - logo_height) // 2

        x_white = ((img_width - logo_width) // (2 * args.scale)) * args.scale
        y_white = ((img_height - logo_height) // (2 * args.scale)) * args.scale

        white_width = img_width - 2 * x_white
        white_height = img_height - 2 * y_white

        white = Image.new(mode="RGB", size=(white_width, white_height), color=WHITE)

        white.paste(logo, (x - x_white, y - y_white), logo)
        img.paste(white, (x_white, y_white))

    # Add margins.
    if args.margin > 0:
        width, height = img.size

        white = Image.new(
            mode="RGB",
            size=(width + 2 * args.margin, height + 2 * args.margin),
            color=WHITE)

        white.paste(img, (args.margin, args.margin))
        img = white

    # Output the QR code image.
    if args.file is not None:
        img.save(args.file)
    else:
        img.show()