from lark import Transformer

from va import VA


class ASTtoNFA(Transformer):
    def __init__(self, *args, **kwargs):
        # Each atom of the expression is expressed with a unique id, atom[id]
        # is the character class actually matched by the atom
        self.nb_atoms = 0
        self.atom = dict()

        super().__init__(*args, **kwargs)

    def register_atom(self, charclass):
        self.nb_atoms += 1
        atom_id = self.nb_atoms
        self.atom[atom_id] = charclass
        return atom_id

    def start(self, sub):
        P, D, F, G = sub[0]

        transitions = (
            [(source, self.atom[target], target) for source, target in D]
            + [(0, self.atom[target], target) for target in P])
        finals = F if not G else F | {0}

        return VA(self.nb_atoms + 1, transitions, finals)

    def concatenate(self, sub):
        (lP, lD, lF, lG), (rP, rD, rF, rG) = sub

        P = lP if not lG else lP | rP
        F = rF if not rG else lF | rF
        G = lG and rG

        D = lD | rD

        for prefix in lF:
            for suffix in rP:
                D.add((prefix, suffix))

        return P, D, F, G

    def empty(self, sub):
        return set(), set(), set(), True

    def letter(self, sub):
        char = str(sub[0])
        atom = self.register_atom(char)
        return {atom}, set(), {atom}, False

    def optional(self, sub):
        P, D, F, _ = sub[0]
        return P, D, F, True

    def star(self, sub):
        print(sub)
        P, D, F, _ = sub[0]

        for suffix in P:
            for prefix in F:
                D.add((prefix, suffix))

        return P, D, F, True
