
def fois(a, b):
    r = 0
    while b > 0:
        if b & 1:
            r = r ^ a
        b = b >> 1
        a = a << 1
    return r

def taille(a):
    r = 0
    while a > 0:
        a = a >> 1
        r += 1
    return r

def reduit(a, irreductible):
    taille_irr = taille(irreductible)
    taille_a = taille(a)
    while taille_a >= taille_irr:
        a = a ^ (irreductible << (taille_a - taille_irr))
        taille_a = taille(a)
    return a

class CorpsGalois(object):

    def __init__(self, irreductible=0b100011101):
        taille_irr = taille(irreductible)
        self.nombre = (2 ** (taille_irr - 1)) - 1
        self.exps = [0] * self.nombre
        self.logs = [0] * (self.nombre + 1)

        a = 1
        for i in range(0, self.nombre):
            self.exps[i] = a
            self.logs[a] = i
            a = reduit(fois(a, 2), irreductible)

    def plus(self, a, b):
        return a ^ b

    def fois(self, a, b):
        if a == 0 or b == 0:
            return 0
        return self.exps[(self.logs[a] + self.logs[b]) % self.nombre]

    def division(self, a, b):
        if b == 0:
            raise ZeroDivisionError()
        if a == 0:
            return 0
        return self.exps[(self.logs[a] + self.nombre - self.logs[b]) % self.nombre]

    def puissance(self, a, b):
        if a == 0:
            return 0
        return self.exps[(self.logs[a] * b) % self.nombre]

    def inverse(self, a):
        return self.exps[self.nombre - self.logs[a]]


class CorpsPoly(object):

    def __init__(self, corps):
        self.corps = corps

    def produit_scalaire(self, p, a):
        return [self.corps.fois(e, a) for e in p]

    def fois(self, p, q):
        r = [0] * (len(p) + len(q) - 1)
        for i in range(len(p)):
            for j in range(len(q)):
                produit = self.corps.fois(p[i], q[j])
                r[i + j] = self.corps.plus(r[i + j], produit)
        return r

    def evaluation(self, p, a):
        r = 0
        for i in range(len(p)):
            r = self.corps.plus(self.corps.fois(r, a), p[i])
        return r

    def division(self, p, q):
        if len(q) == 0:
            raise ZeroDivisionError()
        r = []
        while len(p) >= len(q):
            a = self.corps.division(p[0], q[0])
            r.append(a)
            for i in range(1, len(q)):
                p[i] = self.corps.plus(p[i], self.corps.fois(q[i], a))
            p = p[1:]
        return r, p

    def generateur(self, n):
        g = [1]
        for i in range(n):
            g = self.fois(g, [1, self.corps.puissance(2, i)])
        return g

class Encodeur(object):

    def __init__(self, poly, n_extra):
        self.poly = poly
        self.generateur = poly.generateur(n_extra)

    def encode(self, donnees):
        avec_zeros = donnees + [0] * (len(self.generateur) - 1)
        _, extra = self.poly.division(avec_zeros, self.generateur)
        return donnees + extra
