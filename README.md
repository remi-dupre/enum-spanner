Constant-Delay Enumeration for Nondeterministic Document Spanners
=================================================================

This is an implementation of the algorithm published by Amarilli, Bourhis,
Mengel and Niewerth at [ICDT'2019](https://arxiv.org/abs/1807.09320) for
Constant-Delay Enumeration for Nondeterministic Document Spanners

**This code is under development and is not yet usable at that stage.**


Usage
-----

```bash
# Display all occurences of a pattern in a file
src/main.py [pattern] [file]
cat [file] | src/main.py [pattern]

# This example will match 'aa@aa', 'aa@a', 'a@aa', 'a@a'
echo "aa@aa" | src/main.py ".+@.+"

# Run unit tests
make tests
```

Displayed matches will correspond to all distincts substrings of the text that
match the given pattern, if the pattern contains named groups, it will also
output one match for each possible assignation of the groups.


Supported Regular Expression
----------------------------

All the supported grammar can be found in [grammar.py](src/regexp/grammar.py).


Dependencies
------------

Dependencies are specified in `requirements.txt`, you can install them manually
or setup a virtualenv:

```bash
python -m venv .venv
source .venv/bin/activate  # run this at any time you restarted a shell
pip install -U -r requirements.txt
```
