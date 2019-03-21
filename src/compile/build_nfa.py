from va import VA


def letter(letter: str) -> VA:
    return VA(2, [(0, letter, 1), 1])

def concatenation(nfa1: VA, nfa2: VA) -> VA:
    ret = VA(nfa1.nb_states + nfa2.nb_states,
             nfa1.transitions.copy())

    for source, label, target in nfa2.transitions:
        ret.transitions.append((source + nfa1.nb_states, label,
                                target + nfa1.nb_states))

    ret.transitions.append((nfa1.final, None, nfa1.nb_states))
    return ret
