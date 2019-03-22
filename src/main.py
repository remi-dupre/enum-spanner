#!/usr/bin/python3
import argparse
import sys

import regexp
from enum_mappings import enum_matches


# ----- Parse Command Line Arguments -----

parser = argparse.ArgumentParser(
    description='Enumerate all matches of a regular expression on a text.')

parser.add_argument(
    'regexp', type=str, help='the pattern to look for')
parser.add_argument(
    'file', type=argparse.FileType('w'), nargs='?', default=sys.stdin,
    help='the file to be read, if none is specified, STDIN is used')

args = parser.parse_args()


# ----- Match The Expression -----

pattern = regexp.compile(args.regexp)
document = args.file.read()

if document[-1] == '\n':
    document = document[:-1]

for count, match in enumerate(enum_matches(pattern, document)):
    print(f'{count}: ', end='')
    match.pretty_print()
