
def times(a, b):
    """Multiplication of GF(2) polynomials."""

    r = 0
    while b > 0:
        if b & 1:
            r = r ^ a
        b = b >> 1
        a = a << 1
    return r

def degree(a):
    """Degree of a GF(2) polynomial."""

    r = -1
    while a > 0:
        a = a >> 1
        r += 1
    return r

def modulo(a, b):
    """Modulo of GF(2) polynomials."""

    degree_b = degree(b)
    degree_a = degree(a)
    while degree_a >= degree_b:
        a = a ^ (b << (degree_a - degree_b))
        degree_a = degree(a)
    return a

class GaloisField(object):
    """Galois field specified by an irreducible polynomial over GF(2)."""

    def __init__(self, irreducible):
        degree_irr = degree(irreducible)
        self.modulus = (1 << degree_irr) - 1
        self.exps = [0] * self.modulus
        self.logs = [0] * (self.modulus + 1)

        a = 1
        for i in range(0, self.modulus):
            self.exps[i] = a
            self.logs[a] = i
            a = modulo(times(a, 2), irreducible)

    def plus(self, a, b):
        """Addition."""

        return a ^ b
    
    def minus(self, a, b):
        """Subtraction."""

        return a ^ b

    def times(self, a, b):
        """Multiplication."""

        if a == 0 or b == 0:
            return 0
        return self.exps[(self.logs[a] + self.logs[b]) % self.modulus]

    def division(self, a, b):
        """Division."""

        if b == 0:
            raise ZeroDivisionError()
        if a == 0:
            return 0
        return self.exps[(self.logs[a] - self.logs[b]) % self.modulus]

    def power(self, a, b):
        """Power."""

        if a == 0:
            return 0
        return self.exps[(self.logs[a] * b) % self.modulus]

    def inverse(self, a):
        """Inverse."""

        if a == 0:
            raise ZeroDivisionError()
        return self.exps[self.modulus - self.logs[a]]


class PolyRing(object):
    """Polynomial commutative ring over a finite field.
    
    This class assumes that the finite field has:
    - 0 as the additive neutral element
    - 1 as the multiplicative neutral element
    - 2 as a generator.
    """

    def __init__(self, field):
        self.field = field

    def times(self, p, q):
        """Multiplication."""

        r = [0] * (len(p) + len(q) - 1)
        for i in range(len(p)):
            for j in range(len(q)):
                produit = self.field.times(p[i], q[j])
                r[i + j] = self.field.plus(r[i + j], produit)
        return r

    def evaluation(self, p, a):
        """Evaluation of a polynomial at a given point."""

        r = 0
        for i in range(len(p)):
            r = self.field.plus(self.field.times(r, a), p[i])
        return r

    def division(self, p, q):
        """Division with remainder."""

        if len(q) == 0:
            raise ZeroDivisionError()
        r = []
        while len(p) >= len(q):
            a = self.field.division(p[0], q[0])
            r.append(a)
            for i in range(1, len(q)):
                p[i] = self.field.minus(p[i], self.field.times(q[i], a))
            p.pop(0)
        return r, p

    def generator(self, n):
        g = [1]
        for i in range(n):
            g = self.times(g, [1, self.field.power(2, i)])
        return g

class Encoder(object):
    """Error correction encoder."""

    def __init__(self, n_extra, irreducible):
        self.poly_ring = PolyRing(GaloisField(irreducible))
        self.generator = self.poly_ring.generator(n_extra)

    def encode(self, data):
        padded = data + [0] * (len(self.generator) - 1)
        _, extra = self.poly_ring.division(padded, self.generator)
        return extra
