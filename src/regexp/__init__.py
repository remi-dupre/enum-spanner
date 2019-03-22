from regexp.grammar import build_ast
from regexp.glushkov import ASTtoNFA
from mapping import match_of_mapping
from va import VA


def compile(regexp: str) -> VA:
    '''
    Compile a regexp to a non-deterministic variable automata.
    '''
    regexp = f'(?P<match>{regexp}).*'
    tree = build_ast(regexp)
    return ASTtoNFA().transform(tree)

def match(regexp: str, document) -> VA:
    from enum_mappings import enum_mappings
    automata = compile(regexp)
    return next(enum_mappings(automata, document))
