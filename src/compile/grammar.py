import logging
from lark import Lark

logging.basicConfig(level=logging.DEBUG)


GRAMMAR = '''
    start: empty
         | expression

    empty:

    ?charclass: LETTER "-" LETTER                           -> range

    ?atom: LETTER                                           -> letter
        | "[" charclass* "]"                                -> charclass
        | "."                                               -> wildcard

    ?expression: atom
               | expression expression                      -> concatenate
               | expression "|" expression                  -> union
               | expression "*"                             -> star
               | expression "?"                             -> optional
               | "(" expression ")"

    %import common.LETTER
'''

# Build the AST, given an input regexp
build_ast = Lark(GRAMMAR, parser='lalr', debug=True).parse
