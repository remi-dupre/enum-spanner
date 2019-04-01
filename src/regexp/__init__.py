import benchmark
from enum_mappings import enum_mappings
from regexp.ast import EnumerateVariables
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
    has_strong_begin = False
    has_strong_end = False

    if regexp and regexp[0] == '^':
        regexp = regexp[1:]
        has_strong_begin = True

    if regexp and regexp[-1] == '$':
        regexp = regexp[:-1]
        has_strong_end = True

    if 'match' not in variables(regexp):
        regexp = f'(?P<match>{regexp})'

    if not has_strong_begin:
        regexp = '.*' + regexp

    if not has_strong_end:
        regexp = regexp + '.*'

    tree = parser(regexp)
    return ASTtoNFA().transform(tree)


def match(regexp: str, document) -> VA:
    automata = compile(regexp)

    try:
        return next(enum_mappings(automata, document))
    except StopIteration:
        return None

def variables(regexp: str) -> set:
    tree = parser(regexp)
    return EnumerateVariables().transform(tree)
