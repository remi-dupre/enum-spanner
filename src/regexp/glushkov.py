from lark import Transformer

import atoms
from mapping import Variable
from va import VA


class ASTtoNFA(Transformer):
    def __init__(self, *args, **kwargs):
        # Each atom of the expression is expressed with a unique id, atom[id]
        # is the character class actually matched by the atom
        self.nb_atoms = 0
        self.atoms = dict()

        super().__init__(*args, **kwargs)

    def register_atom(self, atom):
        self.nb_atoms += 1
        atom_id = self.nb_atoms
        self.atoms[atom_id] = atom
        return atom_id

    def regexp(self, sub):
        P, D, F, G = sub[0]

        transitions = (
            [(source, self.atoms[target], target) for source, target in D]
            + [(0, self.atoms[target], target) for target in P])
        finals = F if not G else F | {0}

        return VA(self.nb_atoms + 1, transitions, finals)

    def concatenation(self, sub):
        print(sub)
        (lP, lD, lF, lG), (rP, rD, rF, rG) = sub

        P = lP if not lG else lP | rP
        F = rF if not rG else lF | rF
        G = lG and rG

        D = lD | rD

        for prefix in lF:
            for suffix in rP:
                D.add((prefix, suffix))

        return P, D, F, G

    def charclass(self, sub):
        atom = self.register_atom(atoms.CharClass(sub))
        return {atom}, set(), {atom}, False

    def charclass_complement(self, sub):
        atom = self.register_atom(atoms.CharClassComplement(sub))
        return {atom}, set(), {atom}, False

    def class_escaped_char(self, sub):
        return str(sub[0]), str(sub[0])

    def class_normal_char(self, sub):
        return str(sub[0]), str(sub[0])

    def empty(self, sub):
        return set(), set(), set(), True

    def escaped_char(self, sub):
        char = str(sub[0])
        atom = self.register_atom(atoms.Char(char))
        return {atom}, set(), {atom}, False

    def named_group(self, sub):
        name, (P, D, F, G) = sub

        variable = Variable(str(name))
        open_id = self.register_atom(variable.marker_open())
        close_id = self.register_atom(variable.marker_close())

        nP = {open_id}
        nD = (D
              | {(open_id, target) for target in P}
              | {(source, close_id) for source in F})
        nF = {close_id}
        nG = False

        if G:
            nD.add((open_id, close_id))

        return nP, nD, nF, nG

    def normal_char(self, sub):
        char = str(sub[0])
        atom = self.register_atom(atoms.Char(char))
        return {atom}, set(), {atom}, False

    def optional(self, sub):
        P, D, F, _ = sub[0]
        return P, D, F, True

    def range(self, sub):
        return tuple(map(str, sub))

    def star(self, sub):
        P, D, F, _ = sub[0]

        for suffix in P:
            for prefix in F:
                D.add((prefix, suffix))

        return P, D, F, True

    def union(self, sub):
        (lP, lD, lF, lG), (rP, rD, rF, rG) = sub

        P = lP | rP
        F = lF | rF
        D = lD | rD
        G = lG or rG

        return P, D, F, G

    def wildcard(self, sub):
        atom = self.register_atom(atoms.Wildcard())
        return {atom}, set(), {atom}, False
