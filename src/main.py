#!/usr/bin/python3
import argparse
import signal
import sys
from termcolor import cprint

import benchmark
import regexp
from enum_mappings import compile_matches, enum_matches


sys.setrecursionlimit(10**4)

# ----- Parse Command Line Arguments -----

parser = argparse.ArgumentParser(
    description='Enumerate all matches of a regular expression on a text.')


parser.set_defaults(count=False)
parser.set_defaults(debug=True)
parser.set_defaults(display_offset=False)
parser.set_defaults(only_matching=False)
parser.set_defaults(only_groups=False)
parser.set_defaults(print=True)
parser.set_defaults(show_automata=False)
parser.set_defaults(show_graph=False)


parser.add_argument(
    'regexp', type=str, help='the pattern to look for')

parser.add_argument(
    'file', type=argparse.FileType('w'), nargs='?', default=sys.stdin,
    help='The file to be read, if none is specified, STDIN is used')

parser.add_argument(
    '-b', '--byte-offset', dest='display_offset', action='store_true',
    help='Print the 0-based offset of each matching part and groups.')

parser.add_argument(
    '-c', '--count', dest='count', action='store_true',
    help='Display the number of matches instead.')

parser.add_argument(
    '-d', '--debug', dest='debug', action='store_true',
    help='Display debug information.')

parser.add_argument(
    '-o', '--only-matching', dest='only_matching', action='store_true',
    help='Print only the matched (non-empty) parts of a matching line, with '
         'each such part on a separate output line.')

parser.add_argument(
    '-O', '--only-groups', dest='only_groups', action='store_true',
    help='Print only the matched (non-empty) groups')

parser.add_argument(
    '-p', '--no-print', dest='print', action='store_false',
    help='Prevent the display of a substring for each match.')

parser.add_argument(
    '--no-debug', dest='debug', action='store_false',
    help='Don\'t display debug information.')

parser.add_argument(
    '--show-automata', dest='show_automata', action='store_true',
    help='Display the automata built out of the input regexp.')

parser.add_argument(
    '--show-dag', '--show-graph', dest='show_graph', action='store_true',
    help='Display the dag built out of the input regexp.')

args = parser.parse_args()

# ----- Read inputs -----

pattern = regexp.compile(args.regexp)
document = args.file.read()

if document[-1] == '\n':
    document = document[:-1]


# ----- Special Actions -----

if args.show_automata:
    pattern = regexp.compile(args.regexp)
    pattern.render('automata', display=True)

if args.show_graph:
    dag = compile_matches(pattern, document)
    dag.render('dag', document=document, display=True)


# ----- Match The Expression -----

if args.count:
    print(sum(1 for _ in enum_matches(pattern, document)))
else:
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    for count, match in enumerate(enum_matches(pattern, document)):
        if args.display_offset or not args.print:
            print(f'{match.span[0]},{match.span[1]}', end='')

            for name, span in match.group_spans.items():
                print(f' {name}={span[0]},{span[1]}', end='')

            if args.print:
                print(': ', end='')

        if args.only_groups:
            for name in match.group_spans:
                if match.group(name):
                    print(f'{name}=', end='')
                    cprint(match.group(name), 'red', attrs=['bold', 'dark'],
                           end=' ')

            print()

        elif args.print:
            match.pretty_print(args.only_matching)
        else:
            print()


# ----- Print Debug Infos -----

if args.debug:
    print('----- Debug Infos -----')
    benchmark.print_tracking()
