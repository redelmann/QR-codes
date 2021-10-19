from PIL import Image

from galois import *

def affiche_blanc(img, i, j):
    if i >= 0 and i < 21 and j >= 0 and j < 21:
        img.putpixel((i, j), 1)

def affiche_marqueur(img, i, j):
    for k in range(5):
        affiche_blanc(img, i + 1, j + 1 + k)
    for k in range(5):
        affiche_blanc(img, i + 5, j + 1 + k)
    for k in range(5):
        affiche_blanc(img, i + 1 + k, j + 1)
    for k in range(5):
        affiche_blanc(img, i + 1 + k, j + 5)
    for k in range(9):
        affiche_blanc(img, i - 1, j - 1 + k)
    for k in range(9):
        affiche_blanc(img, i + 7, j - 1 + k)
    for k in range(9):
        affiche_blanc(img, i - 1 + k, j - 1)
    for k in range(9):
        affiche_blanc(img, i - 1 + k, j + 7)

def affiche_format(img, data):
    for k in range(6):
        if data[k] == 0:
            affiche_blanc(img, k, 8)
    for k in range(2):
        if data[6 + k] == 0:
            affiche_blanc(img, 7 + k, 8)
    if data[8] == 0:
        affiche_blanc(img, 8, 7)
    for k in range(6):
        if data[9 + k] == 0:
            affiche_blanc(img, 8, 5 - k)

    for k in range(7):
        if data[k] == 0:
            affiche_blanc(img, 8, 20 - k)
    for k in range(8):
        if data[7 + k] == 0:
            affiche_blanc(img, 13 + k, 8)

MODE_M = 0
MODE_L = 1
MODE_H = 2
MODE_Q = 3

MODES_LONGUEURS = [
    (16, 10),
    (19, 7),
    (9, 17),
    (13, 13),
]

def format(mode, masque):
    donnees = ((mode << 3) + masque) << 10
    correcteurs = reduit(donnees, 0b10100110111)
    avec_masque = (donnees + correcteurs) ^ 0b101010000010010
    return en_bits(avec_masque, 15)

MASQUES = [
    lambda i, j: (i + j) % 2,
    lambda i, j: j % 2,
    lambda i, j: i % 3,
    lambda i, j: (i + j) % 3,
    lambda i, j: ((j // 2) + (i // 3)) % 2,
    lambda i, j: ((i * j) % 2) + ((i * j) % 3),
    lambda i, j: ((i * j) % 3 + i * j) % 2,
    lambda i, j: ((i * j) % 3 + i + j) % 2,
]

def applique_masque(masque, i, j, bit):
    m = 1 if MASQUES[masque](i, j) == 0 else 0
    return bit ^ m

def monte(i, j):
    return [(i + 1 - di, j + 3 - dj) for dj in range(4) for di in range(2)]

def monte_special(i, j):
    bas = [(i + 1 - di, j + 4 - dj) for dj in range(2) for di in range(2)]
    haut = [(i + 1 - di, j + 1 - dj) for dj in range(2) for di in range(2)]
    return bas + haut

def descend(i, j):
    return [(i + 1 - di, j + dj) for dj in range(4) for di in range(2)]

def descend_special(i, j):
    haut = [(i + 1 - di, j + dj) for dj in range(2) for di in range(2)]
    bas = [(i + 1 - di, j + 3 + dj) for dj in range(2) for di in range(2)]
    return haut + bas

POSITIONS_BITS = [bit for bits in [
    monte(19, 17),
    monte(19, 13),
    monte(19, 9),
    descend(17, 9),
    descend(17, 13),
    descend(17, 17),
    monte(15, 17),
    monte(15, 13),
    monte(15, 9),
    descend(13, 9),
    descend(13, 13),
    descend(13, 17),
    monte(11, 17),
    monte(11, 13),
    monte(11, 9),
    monte_special(11, 4),
    monte(11, 0),
    descend(9, 0),
    descend_special(9, 4),
    descend(9, 9),
    descend(9, 13),
    descend(9, 17),
    monte(7, 9),
    descend(4, 9),
    monte(2, 9),
    descend(0, 9),
] for bit in bits]

def en_bits(octet, taille=8):
    return [1 if octet & (1 << (taille - 1 - i)) else 0 for i in range(taille)]

def en_nombre(bits):
    r = 0
    for bit in bits:
        r = r << 1
        r = r + bit
    return r

def affiche_donnees(img, donnees, masque):
    assert(len(donnees) * 8 == len(POSITIONS_BITS))
    bits = [bit for octet in donnees for bit in en_bits(octet)]

    for (bit, position) in zip(bits, POSITIONS_BITS):
        (i, j) = position
        v = applique_masque(masque, i, j, bit)
        if v == 0:
            affiche_blanc(img, i, j)

ENC_NUMERIQUE = 0
ENC_ALPHANUMERIQUE = 1
ENC_OCTET = 2
ENC_KANJI = 3

ENC_CODE = [
    en_bits(1, 4),
    en_bits(2, 4),
    en_bits(4, 4),
    en_bits(8, 4),
    en_bits(7, 4),
]

ENC_TAILLE_BITS = [
    10,
    9,
    8,
    8,
]

def encode_numerique(chaine):
    for c in chaine:
        if c < '0' or c > '9':
            raise ValueError("Invalide !")

    bits = []
    while len(chaine) > 0:
        k = min(len(chaine), 3)
        partie = int(chaine[:k])
        chaine = chaine[k:]

        if k == 1:
            bits.extend(en_bits(partie, 4))
        elif k == 2:
            bits.extend(en_bits(partie, 7))
        else:
            bits.extend(en_bits(partie, 10))
    return bits

def encode_alphanumerique(chaine):
    speciaux = " $%*+-./:"

    def encode_char(c):
        if c >= '0' and c <= '9':
            return ord(c) - ord('0')
        if c >= 'A' and c <= 'Z':
            return ord(c) - ord('A') + 10
        if c in speciaux:
            return speciaux.index(c) + 36
        raise ValueError("Invalide !")

    bits = []
    while len(chaine) > 0:
        k = min(len(chaine), 2)
        partie = chaine[:k]
        chaine = chaine[k:]

        if k == 2:
            a = encode_char(partie[0]) * 45
            b = encode_char(partie[1])
            bits.extend(en_bits(a + b, 11))
        else:
            a = encode_char(partie[0])
            bits.extend(en_bits(a, 6))
    return bits

def encode_octets(chaine):
    try:
        bits = []
        for octet in chaine.encode("iso-8859-1"):
            bits.extend(en_bits(octet))
        return bits
    except:
        raise ValueError("Invalide !") from None

def encode_kanji(chaine):
    bits = []
    octets = chaine.encode("shift-jis")
    while len(octets) > 0:
        k = min(len(octets), 2)
        partie = octets[:k]
        octets = octets[k:]

        if k == 2:
            a = partie[0] << 8
            b = partie[1]
            double_octet = a + b

            if double_octet >= 0x8140 and double_octet <= 0x9FFC:
                double_octet -= 0x8140
            elif double_octet >= 0xE040 and double_octet <= 0xEBBF:
                double_octet -= 0xC140
            else:
                raise ValueError("Invalide !")

            a = double_octet >> 8
            b = double_octet & ((2 ** 8) - 1)
            bits.extend(en_bits(a * 0xC0 + b, 13))
        else:
            raise ValueError("Invalide !")
    return bits

ENC_FONCTIONS = [
    encode_numerique,
    encode_alphanumerique,
    encode_octets,
    encode_kanji,
]

PAD_BITS = [
    en_bits(236),
    en_bits(17),
]

def encode_chaine(chaine, mode, enc):
    nombre = len(chaine)
    bits = []
    bits.extend(ENC_CODE[enc])
    bits.extend(en_bits(nombre, ENC_TAILLE_BITS[enc]))
    bits.extend(ENC_FONCTIONS[enc](chaine))

    (longeur_donnees, longeur_correcteurs) = MODES_LONGUEURS[mode]
    requis = longeur_donnees * 8

    if len(bits) > requis:
        raise ValueError("Chaine trop longue !")

    nombre_pad = min(4, requis - len(bits))
    bits.extend([0] * nombre_pad)

    extra = len(bits) % 8
    if extra > 0:
        bits.extend([0] * (8 - extra))

    i = 0
    while len(bits) != requis:
        bits.extend(PAD_BITS[i])
        i = (i + 1) % 2

    octets = []
    while len(bits) > 0:
        octets.append(en_nombre(bits[:8]))
        bits = bits[8:]

    encodeur = Encodeur(CorpsPoly(CorpsGalois()), longeur_correcteurs)

    return encodeur.encode(octets)

def creer_qr(message, mode, masque, enc):
    img = Image.new(mode="1", size=(21,21))
    affiche_marqueur(img, 0, 0)
    affiche_marqueur(img, 14, 0)
    affiche_marqueur(img, 0, 14)
    affiche_blanc(img, 6, 9)
    affiche_blanc(img, 6, 11)
    affiche_blanc(img, 9, 6)
    affiche_blanc(img, 11, 6)
    affiche_format(img, format(mode, masque))
    donnees = encode_chaine(message, mode, enc)
    affiche_donnees(img, donnees, masque)
    return img
