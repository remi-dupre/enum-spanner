#!/usr/bin/python3
import argparse
import sys

import benchmark
import regexp
from enum_mappings import enum_matches


sys.setrecursionlimit(10**4)

# ----- Parse Command Line Arguments -----

parser = argparse.ArgumentParser(
    description='Enumerate all matches of a regular expression on a text.')


parser.set_defaults(count=False)
parser.set_defaults(debug=True)
parser.set_defaults(display_offset=False)
parser.set_defaults(only_matching=False)
parser.set_defaults(print=True)
parser.set_defaults(show_automata=False)


parser.add_argument(
    'regexp', type=str, help='the pattern to look for')

parser.add_argument(
    'file', type=argparse.FileType('w'), nargs='?', default=sys.stdin,
    help='the file to be read, if none is specified, STDIN is used')

parser.add_argument(
    '-b', '--byte-offset', dest='display_offset', action='store_true',
    help='Print the 0-based offset of each matching part and groups.')

parser.add_argument(
    '-c', '--count', dest='count', action='store_true',
    help='display the number of matches instead')

parser.add_argument(
    '-d', '--debug', dest='debug', action='store_true',
    help='display debug information')

parser.add_argument(
    '-o', '--only-matching', dest='only_matching', action='store_true',
    help='Print only the matched (non-empty) parts of a matching line, with '
         'each such part on a separate output line.')

parser.add_argument(
    '-p', '--no-print', dest='print', action='store_false',
    help='Prevent the display of a substring for each match')

parser.add_argument(
    '--no-debug', dest='debug', action='store_false',
    help='don\'t display debug information')

parser.add_argument(
    '--show-automata', dest='show_automata', action='store_true',
    help='display the automata built out of the input regexp instead')

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
        if args.display_offset or not args.print:
            print(f'{match.span[0]},{match.span[1]}', end='')

            for name, span in match.group_spans.items():
                print(f' {name}={span[0]},{span[1]}', end='')

            if args.print:
                print(': ', end='')

        if args.print:
            match.pretty_print(args.only_matching)
        else:
            print()


# ----- Print Debug Infos -----

if args.debug:
    print('----- Debug Infos -----')
    benchmark.print_tracking()
