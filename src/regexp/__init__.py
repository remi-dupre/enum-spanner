from regexp.grammar import build_ast
from regexp.glushkov import ASTtoNFA
from va import VA


def compile(regexp: str) -> VA:
    '''
    Compile a regexp to a non-deterministic variable automata.
    '''
    tree = build_ast(regexp)
    print(tree.pretty())
    return ASTtoNFA().transform(tree)
