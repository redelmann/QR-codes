from qr import *
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='QR codes generator.')
    parser.add_argument('string',
        type=str,
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
        const=1,
        default=1,
        nargs='?',
        help='QR version')

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

    img = make_qr_code(args.string, mode, args.mask, enc, args.version)

    if args.scale > 1:
        width, height = img.size
        img = img.resize((args.scale * width, args.scale * height), resample=Image.BOX)

    if args.file is not None:
        img.save(args.file)
    else:
        img.show()