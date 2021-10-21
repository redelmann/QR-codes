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

    args = parser.parse_args()

    enc = {
        'byte': ENC_BYTE,
        'alpha': ENC_ALPHANUMERIC,
        'num': ENC_NUMERIC,
        'kanji': ENC_KANJI,
    }[args.enc]

    mode = {
        'L': MODE_L,
        'M': MODE_M,
        'Q': MODE_Q,
        'H': MODE_H,
    }[args.mode]

    message = args.string
    if message is None:
        message = sys.stdin.read()

    img = make_qr_code(message, mode, args.mask, enc, args.version)

    if args.scale > 1:
        width, height = img.size
        img = img.resize((args.scale * width, args.scale * height), resample=Image.BOX)

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

    if args.file is not None:
        img.save(args.file)
    else:
        img.show()