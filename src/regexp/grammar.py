import logging
from lark import Lark

logging.basicConfig(level=logging.DEBUG)


GRAMMAR = '''
    start: union

    empty:

    // General expression
    ?union: concatenation ( "|" union )?
          | empty ( "|" union )?

    // Expression with no union
    ?concatenation: simple ( concatenation )?

    // Expression with no union and no concatenation
    ?simple: elementary
           | elementary "*"                             -> star
           | elementary "?"                             -> optional

    // An expression that can be considered as one block
    ?elementary: atom
               | "(" union ")"
               | "(?P<" NAME ">" union  ")"             -> named_group

    // Match one atomic letter
    ?atom: LETTER                                           -> letter
        | "[" charclass* "]"                                -> charclass
        | "."                                               -> wildcard

    // Range of letters
    ?charclass: LETTER "-" LETTER                           -> range

    %import common.LETTER
    %import common.CNAME -> NAME
'''

# Build the AST, given an input regexp
build_ast = Lark(GRAMMAR, parser='lalr', debug=True).parse
