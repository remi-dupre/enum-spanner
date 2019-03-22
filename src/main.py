#!/usr/bin/python3
import argparse
import sys

import benchmark
import regexp
from enum_mappings import enum_matches


# ----- Parse Command Line Arguments -----

parser = argparse.ArgumentParser(
    description='Enumerate all matches of a regular expression on a text.')


parser.set_defaults(debug=True)
parser.set_defaults(count=False)
parser.set_defaults(show_automata=False)


parser.add_argument(
    'regexp', type=str, help='the pattern to look for')

parser.add_argument(
    'file', type=argparse.FileType('w'), nargs='?', default=sys.stdin,
    help='the file to be read, if none is specified, STDIN is used')

parser.add_argument(
    '-c', '--count', dest='count', action='store_true',
    help='display the count of match instead')

parser.add_argument(
    '-d', '--debug', dest='debug', action='store_true',
    help='display debug informations')
parser.add_argument(
    '--no-debug', dest='debug', action='store_false',
    help='don\'t display debug informations')

parser.add_argument(
    '--show-automata', dest='show_automata', action='store_true',
    help='display the automata built out of the imput regexp instead')

args = parser.parse_args()


# ----- Special Actions -----

if args.show_automata:
    pattern = regexp.compile(args.regexp)
    pattern.render('automata', display=True)


# ----- Match The Expression -----

pattern = regexp.compile(args.regexp)

document = args.file.read()

if document[-1] == '\n':
    document = document[:-1]

if args.count:
    print(sum(1 for _ in enum_matches(pattern, document)))
else:
    for count, match in enumerate(enum_matches(pattern, document)):
        print(f'{count}: ', end='')
        match.pretty_print()


# ----- Print Debug Infos -----

if args.debug:
    print('----- Debug Infos -----')
    benchmark.print_tracking()
