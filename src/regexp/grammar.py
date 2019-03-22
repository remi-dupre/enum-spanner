import logging
from lark import Lark, Transformer, Tree

logging.basicConfig(level=logging.DEBUG)


SPECIAL_CHARS = ['/', '(', ')', '[', ']', '\\', '|', '*', '+', '?', '.']
SPECIAL_CHARS_ESCAPED = ''.join('\\' + char for char in SPECIAL_CHARS)

CLASS_SPECIAL_CHARS = ['/', '^', '[', ']', '\\', '-']
CLASS_SPECIAL_CHARS_ESCAPED = ''.join('\\' + char for char in SPECIAL_CHARS)

GRAMMAR = f'''
    regexp: union

    empty:

    // General expression
    ?union: (concatenation | empty) ["|" union]

    // Expression with no union
    ?concatenation: simple (concatenation)?

    // Expression with no union and no concatenation
    ?simple: elementary
           | elementary "+"                                 -> plus
           | elementary "*"                                 -> star
           | elementary "?"                                 -> optional

    // An expression that can be considered as one block
    ?elementary: atom
               | "(" union ")"
               | "(?P<" NAME ">" union  ")"                 -> named_group

    // Match one atomic letter
    ?atom: char
         | "[" (range | singleton)* "]"                     -> charclass
         | "[^" (range | singleton)* "]"                    -> charclass_complement
         | "."                                              -> wildcard

    ?char: normal_char
         | escaped_char

    // Characters that don't need to be escaped
    normal_char: /[^{SPECIAL_CHARS_ESCAPED}]/
    class_normal_char: /[^(?!-){CLASS_SPECIAL_CHARS_ESCAPED}](?!-)/

    // An escaped char, can have various interpretations
    escaped_char: "\\\\" /./
    class_escaped_char: "\\\\" /./

    // Range of letters
    range: UCASE_LETTER "-" UCASE_LETTER
         | LCASE_LETTER "-" LCASE_LETTER
         | DIGIT "-" DIGIT

    ?singleton: class_normal_char
              | class_escaped_char

    %import common.DIGIT
    %import common.LCASE_LETTER
    %import common.UCASE_LETTER
    %import common.CNAME -> NAME
'''


def parse_from(start: str, regexp: str):
    return Lark(GRAMMAR, parser='lalr', debug=True, start=start).parse(regexp)

# May be common and easily added:
#  - quotes (\Q ... \E)
SPECIAL_CHARS_REWRITE = {
    'n': parse_from('char', '\n'),
    'r': parse_from('char', '\r'),
    't': parse_from('char', '\t'),
    '0': parse_from('char', '\0'),
    'b': parse_from('char', '\b'),
    's': parse_from('atom', '[\r\n\t]'),
    'S': parse_from('atom', '[^\r\n\t]'),
    'd': parse_from('regexp', '[0-9]'),
    'D': parse_from('atom', '[^0-9]'),
    'w': parse_from('atom', '[a-zA-Z0-9]'),
    'W': parse_from('atom', '[^a-zA-Z0-9_]'),
}

CLASS_SPECIAL_CHARS_REWRITE = {
    'n': parse_from('singleton', '\n'),
    'r': parse_from('singleton', '\r'),
    't': parse_from('singleton', '\t'),
    '0': parse_from('singleton', '\0'),
    'b': parse_from('singleton', '\b'),
    'd': parse_from('range', '0-9'),
}


class RewriteSpecials(Transformer):
    def escaped_char(self, subtree):
        char = str(subtree[0])

        if char in SPECIAL_CHARS_REWRITE:
            return SPECIAL_CHARS_REWRITE[char]

        return Tree('escaped_char', subtree)

    def class_escaped_char(self, subtree):
        char = str(subtree[0])
        if char in CLASS_SPECIAL_CHARS_REWRITE:
            return CLASS_SPECIAL_CHARS_REWRITE[char]

        return Tree('class_escaped_char', subtree)


# Build the AST, given an input regexp
parser = Lark(GRAMMAR, parser='lalr', debug=True, start='regexp').parse

def build_ast(regexp: str):
    ret = RewriteSpecials().transform(parser(regexp))
    return ret
