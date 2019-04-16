from collections import deque

import tqdm

from benchmark import track
from enum_mappings.jump import Jump
from va import VA


class IndexedDag:

    def __init__(self, va: VA, document: str):
        self.va = va
        self.document = document

        self.jump = Jump([self.va.initial], self.va.get_adj_for_assignations())
        levels_iter = tqdm.trange(len(self.document),
                                  desc='preprocessing',
                                  unit='B', unit_scale=True,
                                  dynamic_ncols=True)

        for curr_level in levels_iter:
            curr_letter = self.document[curr_level]
            self.jump.next_layer(self.va.get_adj_for_char(curr_letter),
                                 self.va.get_adj_for_assignations())

            # Clean the level at exponential depth
            depth = curr_level & -curr_level

            for level in range(curr_level, curr_level - depth, -1):
                self.jump.clean_layer(level, self.va.get_adj_for_assignations())

    def follow_SpSm(self, gamma: list, Sp: list, Sm: list):
        adj = self.va.get_rev_assignations()
        Sm = set(Sm)
        Sp = set(Sp)
        path_set = {state: set() for state in gamma}
        queue = deque(gamma.copy())

        while queue:
            source = queue.popleft()

            for label, target in adj[source]:
                if label not in Sm:
                    if target not in path_set:
                        queue.append(target)

                    new_ps = path_set[source].copy()

                    if label in Sp:
                        new_ps.add(label)

                    # If the state has a failure anotation, we can skip it
                    if target in path_set and path_set[target] is None:
                        continue

                    # Keep track of the biggest path set for each vertex of the
                    # level, if two path have incomparable path sets, we may
                    # anotate them with a failure anotation (None)
                    if target not in path_set or new_ps >= path_set[target]:
                        path_set[target] = new_ps
                    elif not (path_set[target] >= new_ps
                              or path_set[target] <= new_ps):
                        path_set[target] = None

        print(gamma, Sp, Sm, ' -> ', [vertex for vertex, ps in path_set.items() if ps == Sp])
        return [vertex for vertex, ps in path_set.items() if ps == Sp]

    @track
    def next_level(self, gamma: list):
        adj = self.va.get_rev_assignations()
        K = set()

        # Get list of variables that are part of the level
        stack = gamma.copy()
        mark = set(gamma)

        while stack:
            source = stack.pop()

            for label, target in adj[source]:
                K.add(label)

                if target not in mark:
                    mark.add(target)
                    stack.append(target)

        K = list(K)
        stack = [([], [])]

        while stack:
            Sp, Sm = stack.pop()
            gamma2 = self.follow_SpSm(gamma, Sp, Sm)

            if not gamma2:
                continue

            while len(Sp) + len(Sm) < len(K):
                depth = len(Sp) + len(Sm)
                Sp.append(K[depth])
                gamma2 = self.follow_SpSm(gamma, Sp, Sm)

                if gamma2:
                    new_Sp = Sp.copy()
                    new_Sm = Sm.copy()
                    new_Sm.append(new_Sp.pop())
                    stack.append((new_Sp, new_Sm))
                else:
                    Sm.append(Sp.pop())
                    gamma2 = None

            if gamma2 is None:
                gamma2 = self.follow_SpSm(gamma, Sp, Sm)

            yield list(Sp), gamma2

    def __iter__(self):
        # a stack of pairs (gamma, mapping)
        stack = [(len(self.document), list(self.va.final), [])]

        while stack:
            level, gamma, mapping = stack.pop()

            for Sp, new_gamma in self.next_level(gamma):
                #  print(level, gamma, f' - ({Sp}) ->', new_gamma)
                if not new_gamma:
                    continue

                new_mapping = mapping.copy()
                new_mapping.extend((marker, level) for marker in Sp)

                if level == 0 and self.va.initial in new_gamma:
                    yield new_mapping
                else:
                    #  print(level, new_gamma, end=' -> ')
                    new_level, new_gamma = self.jump(level, new_gamma)
                    #  print(new_level, new_gamma, f'... ({Sp})')
                    if new_gamma:
                        stack.append((new_level, new_gamma, new_mapping))
