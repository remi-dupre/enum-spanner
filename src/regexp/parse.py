from functools import lru_cache
from lark import Lark, Transformer, Tree

import regexp.grammar as grammar


@lru_cache(None)
def get_parser_for(start: str = 'regexp'):
    '''
    Get the parser used to compute the AST from a given non-terminal `start`.
    '''
    return Lark(grammar.GRAMMAR, parser='lalr', start=start)


@lru_cache(100)
def parse_from(start: str, regexp: str):
    '''
    Parse the expression from a given non-terminal.
    '''
    return get_parser_for(start).parse(regexp)


class RewriteSpecials(Transformer):
    '''
    Rewrite the input AST by replacing all expressions that have an equivalent in the given list:
     - grammar.SPECIAL_CHARS_REWRITE
     - grammar.CLASS_SPECIAL_CHARS_REWRITE
    '''

    #pylint: disable=no-self-use
    def escaped_char(self, subtree):
        char = str(subtree[0])

        if char in grammar.SPECIAL_CHARS_REWRITE:
            non_terminal, equivalent = grammar.SPECIAL_CHARS_REWRITE[char]
            return parse_from(non_terminal, equivalent)

        return Tree('escaped_char', subtree)

    def class_escaped_char(self, subtree):
        char = str(subtree[0])

        if char in grammar.CLASS_SPECIAL_CHARS_REWRITE:
            non_terminal, equivalent = grammar.CLASS_SPECIAL_CHARS_REWRITE[char]
            return parse_from(non_terminal, equivalent)

        return Tree('class_escaped_char', subtree)


def parser(regexp: str):
    '''
    Return an AST given a regexp, if the regexp contains some term for which a
    rewrite rule is given in grammar, the term is replaced.
    '''
    ast = parse_from('regexp', regexp)
    ast = RewriteSpecials().transform(ast)
    return ast
