
def times(a, b):
    r = 0
    while b > 0:
        if b & 1:
            r = r ^ a
        b = b >> 1
        a = a << 1
    return r

def size(a):
    r = 0
    while a > 0:
        a = a >> 1
        r += 1
    return r

def modulo(a, irreducible):
    size_irr = size(irreducible)
    size_a = size(a)
    while size_a >= size_irr:
        a = a ^ (irreducible << (size_a - size_irr))
        size_a = size(a)
    return a

class GaloisField(object):

    def __init__(self, irreducible=0b100011101):
        size_irr = size(irreducible)
        self.modulus = (2 ** (size_irr - 1)) - 1
        self.exps = [0] * self.modulus
        self.logs = [0] * (self.modulus + 1)

        a = 1
        for i in range(0, self.modulus):
            self.exps[i] = a
            self.logs[a] = i
            a = modulo(times(a, 2), irreducible)

    def plus(self, a, b):
        return a ^ b

    def times(self, a, b):
        if a == 0 or b == 0:
            return 0
        return self.exps[(self.logs[a] + self.logs[b]) % self.modulus]

    def division(self, a, b):
        if b == 0:
            raise ZeroDivisionError()
        if a == 0:
            return 0
        return self.exps[(self.logs[a] + self.modulus - self.logs[b]) % self.modulus]

    def power(self, a, b):
        if a == 0:
            return 0
        if b < 0:
            return self.exps[((self.logs[a] - self.modulus) * b) % self.modulus]
        return self.exps[(self.logs[a] * b) % self.modulus]

    def inverse(self, a):
        return self.exps[self.modulus - self.logs[a]]


class PolyRing(object):

    def __init__(self, field):
        self.field = field

    def times(self, p, q):
        r = [0] * (len(p) + len(q) - 1)
        for i in range(len(p)):
            for j in range(len(q)):
                produit = self.field.times(p[i], q[j])
                r[i + j] = self.field.plus(r[i + j], produit)
        return r

    def evaluation(self, p, a):
        r = 0
        for i in range(len(p)):
            r = self.field.plus(self.field.times(r, a), p[i])
        return r

    def division(self, p, q):
        if len(q) == 0:
            raise ZeroDivisionError()
        r = []
        while len(p) >= len(q):
            a = self.field.division(p[0], q[0])
            r.append(a)
            for i in range(1, len(q)):
                p[i] = self.field.plus(p[i], self.field.times(q[i], a))
            p = p[1:]
        return r, p

    def generator(self, n):
        g = [1]
        for i in range(n):
            g = self.times(g, [1, self.field.power(2, i)])
        return g

class Encoder(object):

    def __init__(self, poly_ring, n_extra):
        self.poly_ring = poly_ring
        self.generator = poly_ring.generator(n_extra)

    def encode(self, data):
        padded = data + [0] * (len(self.generator) - 1)
        _, extra = self.poly_ring.division(padded, self.generator)
        return data + extra
