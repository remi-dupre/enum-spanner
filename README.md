Constant-Delay Enumeration for Nondeterministic Document Spanners
=================================================================

**This code is under development and is not yet usable at that stage.**

This tool allows you to find efficiently all matches of a regular expression in
a string, i.e., all contiguous substrings that satisfy the regular expression
(including overlapping substrings). It implements the algorithm described in
[Amarilli](https://a3nm.net/), 
[Bourhis](http://cristal.univ-lille.fr/~bourhis/),
[Mengel](http://www.cril.univ-artois.fr/~mengel/) and 
[Niewerth](http://www.theoinf.uni-bayreuth.de/en/team/niewerth_matthias/index.php),
*[Constant-Delay Enumeration for
Nondeterministic Document Spanners](https://arxiv.org/abs/1807.09320)*, ICDT'19.

The algorithm used by the tool is an *enumeration algorithm*. It will first
compile the regular expression into a nondeterministic finite automaton. It will
then preprocess the string (without producing any matches), in time linear in
the string and polynomial in the regular expression. After this precomputation,
the algorithm produces the matches sequentially, with constant *delay* between
each match.

Installation
------------

On a Linux system with Python 3, simply clone this repository, then install the
necessary Python modules described in `requirements.txt`. You can either install
them manually using `pip3`, or setup a virtualenv:

```bash
python -m venv .venv
source .venv/bin/activate  # run this at any time you restarted a shell
pip install -U -r requirements.txt
```

Usage
-----

```bash
# Display all occurences of a pattern in a file
src/main.py [pattern] [file]
cat [file] | src/main.py [pattern]

# This example will match 'aa@aa', 'aa@a', 'a@aa', 'a@a'
echo "aa@aa" | src/main.py ".+@.+"

# Run unit tests
make test
```

The matches display correspond to all distincts substrings of the text that
match the given pattern, if the pattern contains named groups, it will also
output one match for each possible assignation of the groups.


Supported Syntax for Regular Expressions
----------------------------------------

The supported grammar for regular expressions is described in
[grammar.py](src/regexp/grammar.py).


