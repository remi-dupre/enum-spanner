# Invalid characters inside a regular expression
SPECIAL_CHARS = ['/', '(', ')', '[', ']', '{', '}', '\\', '|', '*', '+', '?',
                 '.']
SPECIAL_CHARS_ESCAPED = ''.join('\\' + char for char in SPECIAL_CHARS)

# Invalid characters inside a class definition
CLASS_SPECIAL_CHARS = ['/', '^', '[', ']', '\\', '-']
CLASS_SPECIAL_CHARS_ESCAPED = ''.join('\\' + char for char in CLASS_SPECIAL_CHARS)

# May be common and easily added:
#  - quotes (\Q ... \E)
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
           | elementary "{{" repeat_bounds "}}"             -> repeat

    repeat_bounds: NUMBER
                 | empty "," NUMBER
                 | NUMBER "," empty
                 | NUMBER "," NUMBER

    // An expression that can be considered as one block
    ?elementary: atom
               | "(" union ")"
               | "(?P<" CNAME ">" union  ")"                -> named_group

    // Match one atomic letter
    ?atom: char
         | "[" (range | singleton)* "]"                     -> charclass
         | "[^" (range | singleton)* "]"                    -> charclass_complement
         | "."                                              -> wildcard

    ?char: normal_char
         | escaped_char

    // Characters that don't need to be escaped
    normal_char: /[^{SPECIAL_CHARS_ESCAPED}]/
    class_normal_char: /(?!-)[^{CLASS_SPECIAL_CHARS_ESCAPED}](?!-)/

    // An escaped char, can have various interpretations
    escaped_char: "\\\\" /./
    class_escaped_char: "\\\\" /./

    // Range of letters
    range: UCASE_LETTER "-" UCASE_LETTER
         | LCASE_LETTER "-" LCASE_LETTER
         | DIGIT "-" DIGIT

    ?singleton: class_normal_char
              | class_escaped_char

    %import common.CNAME
    %import common.DIGIT
    %import common.LCASE_LETTER
    %import common.NUMBER
    %import common.UCASE_LETTER
'''

# Equivalent expressions for some shortcut notation for atoms
SPECIAL_CHARS_REWRITE = {
    'n': ('atom', '\n'),
    'r': ('atom', '\r'),
    't': ('atom', '\t'),
    '0': ('atom', '\0'),
    'b': ('atom', '\b'),
    's': ('atom', '[\r\n\t]'),
    'S': ('atom', '[^\r\n\t]'),
    'd': ('atom', '[0-9]'),
    'D': ('atom', '[^0-9]'),
    'w': ('atom', '[a-zA-Z0-9]'),
    'W': ('atom', '[^a-zA-Z0-9_]'),
}

# Equivalent notation for some atoms inside class definitions
CLASS_SPECIAL_CHARS_REWRITE = {
    'n': ('singleton', '\n'),
    'r': ('singleton', '\r'),
    't': ('singleton', '\t'),
    '0': ('singleton', '\0'),
    'b': ('singleton', '\b'),
    'd': ('range', '0-9'),
}
