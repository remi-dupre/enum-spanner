import regexp


# Match maximal blocks of a's
example_1 = regexp.compile('^(.*[^a])?(?P<block_a>a+)([^a].*)?$')

# Match all email address delimited with spaces
example_2 = regexp.compile('\\w+@\\w+')

# Enumerate all subword
example_3 = regexp.compile('.*')

# Enumerate all pairs of a non-empty block of a's followed by a non-empty block
# of b's
example_4 = regexp.compile(
    '^(.*[^a])?(?P<block_a>a+)([^a].*[^b]|[^ab])?(?P<block_b>b+)([^b].*)?$')

# Match email addresses in the form [a.]*@a*.a*
example_5 = regexp.compile('(?P<login>\\w+(\\.\\w+)*)@(?P<server>\\w+\\.\\w+)')


INSTANCES = [
    {
        'name': 'block_a',
        'automata': example_1,
        'documents': ['a', 'aaaaaaaaaaaaa', 'bbbabb', 'aaaabbaaababbbb']
    }, {
        'name': 'sep_email',
        'automata': example_2,
        'documents': ['a bba a@b b@a aaa@bab abbababaa@@@babbabb']
    }, {
        'name': 'substrings',
        'automata': example_3,
        'documents': ['abcdefghijklmnopqrstuvwxyz']
    }, {
        'name': 'ordered_blocks',
        'automata': example_4,
        'documents': ['ab', 'aaaabbbb', 'bbbaaababaaaaaabbbbabbbababbababbabb']
    }, {
        'name': 'mixed_emails',
        'automata': example_5,
        'documents': ['aaaa@aaa.aa', 'aa@aa a@a.a@a.a.a@a.a.a.a@a.a.a.a.a']
    },
]
