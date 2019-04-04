#pylint: disable=no-self-use
from functools import lru_cache
from lark import Lark, Transformer, Token, Tree

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
    Rewrite the input AST by replacing all expressions that have an equivalent
    in the given list:
     - grammar.SPECIAL_CHARS_REWRITE
     - grammar.CLASS_SPECIAL_CHARS_REWRITE
    '''
    def charclass(self, subtree):
        children = sum(([child] if child.data != 'charclass' else child.children
                        for child in subtree), [])
        return Tree('charclass', children)

    def charclass_complement(self, subtree):
        children = sum(([child] if child.data != 'charclass' else child.children
                        for child in subtree), [])
        return Tree('charclass_complement', children)

    def class_escaped_char(self, subtree):
        char = str(subtree[0])

        if char in grammar.CLASS_SPECIAL_CHARS_REWRITE:
            non_terminal, equivalent = grammar.CLASS_SPECIAL_CHARS_REWRITE[char]
            return parse_from(non_terminal, equivalent)

        return Tree('class_escaped_char', subtree)

    def escaped_char(self, subtree):
        char = str(subtree[0])

        if char in grammar.SPECIAL_CHARS_REWRITE:
            non_terminal, equivalent = grammar.SPECIAL_CHARS_REWRITE[char]
            return parse_from(non_terminal, equivalent)

        return Tree('escaped_char', subtree)

    def repeat(self, subtree):
        sub, bounds = subtree

        if len(bounds.children) == 2:
            min_occ, max_occ = bounds.children

            if not isinstance(min_occ, Token):
                assert min_occ.data == 'empty'
                min_occ = 0
            else:
                min_occ = int(min_occ)

            if not isinstance(max_occ, Token):
                assert max_occ.data == 'empty'
                max_occ = None
            else:
                max_occ = int(max_occ)
        else:
            min_occ = max_occ = int(bounds.children[0])

        # Compute separately the case where a star is needed to avoid
        # unnecessary extra states
        if min_occ == 0 and max_occ is None:
            return Tree('star', [sub])

        # Add path for the lower bound
        replacement = Tree('empty', [])

        for i in range(min_occ):
            if i == min_occ-1 and max_occ is None:
                # The last item is a plus if there is no upper bound
                replacement = Tree('concatenation', [replacement,
                                                     Tree('plus', [sub])])
            else:
                replacement = Tree('concatenation', [replacement, sub])

        # Add path to allow the upper bound
        if max_occ is not None:
            optionals = Tree('empty', [])

            for _ in range(max_occ - min_occ):
                optionals = Tree(
                    'optional', [Tree('concatenation', [sub, optionals])])

            replacement = Tree('concatenation', [replacement, optionals])

        return replacement


def parser(regexp: str):
    '''
    Return an AST given a regexp, if the regexp contains some term for which a
    rewrite rule is given in grammar, the term is replaced.
    '''
    ast = parse_from('regexp', regexp)
    ast = RewriteSpecials().transform(ast)
    print(ast.pretty())
    return ast
