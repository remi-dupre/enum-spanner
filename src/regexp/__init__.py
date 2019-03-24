import benchmark
from regexp.parse import parser
from regexp.glushkov import ASTtoNFA
from mapping import match_of_mapping
from va import VA


@benchmark.track
def compile(regexp: str) -> VA:
    '''
    Compile a regexp to a non-deterministic variable automata.
    '''
    # TODO: at least parse ^ and $
    if regexp[0] == '^':
        regexp = '(?P<match>' + regexp[1:]
    else:
        regexp = '.*(?P<match>' + regexp

    if regexp[-1] == '$':
        regexp = regexp[:-1] + ')'
    else:
        regexp = regexp + ').*'

    tree = parser(regexp)
    return ASTtoNFA().transform(tree)


def match(regexp: str, document) -> VA:
    from enum_mappings import enum_mappings
    automata = compile(regexp)

    try:
        return next(enum_mappings(automata, document))
    except StopIteration:
        return None
