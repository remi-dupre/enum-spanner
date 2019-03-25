Constant-Delay Enumeration for Nondeterministic Document Spanners
=================================================================

This tool allows you to find efficiently all matches of a regular expression in
a string, i.e., find all contiguous substrings of the string that satisfy the
regular expression (including overlapping substrings).

**The tool is being actively developed and has not been thoroughly tested yet.
Use at your own risk.**

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

You can then run `src/main.py`.

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
match the given pattern. If the pattern contains named groups, it will also
output one match for each possible assignation of the groups.


Supported Syntax for Regular Expressions
----------------------------------------

The tool supports a subset of the usual regular expression syntax, with several
common operators. The supported grammar for the regular expressions is written
in [grammar.py](src/regexp/grammar.py).


Underlying Algorithm
--------------------

The algorithm used by this tool is described in the research paper
*[Constant-Delay Enumeration for Nondeterministic Document
Spanners](https://arxiv.org/abs/1807.09320)*, by [Amarilli](https://a3nm.net/),
[Bourhis](http://cristal.univ-lille.fr/~bourhis/),
[Mengel](http://www.cril.univ-artois.fr/~mengel/) and
[Niewerth](http://www.theoinf.uni-bayreuth.de/en/team/niewerth_matthias/index.php).
It was presented at the [ICDT'19](http://edbticdt2019.inesc-id.pt/) conference.

The tool will first compile the regular expression into a nondeterministic
finite automaton, and then apply an *enumeration algorithm*. Specifically, it
will first preprocess the string (without producing any matches), in time linear
in the string and polynomial in the regular expression. After this
precomputation, the algorithm produces the matches sequentially, with constant
*delay* between each match.

