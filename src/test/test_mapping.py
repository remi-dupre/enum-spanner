import pytest

import examples
from enum_mappings import enum_mappings, naive_enum_mappings


def test_run_example():
    for example in examples.INSTANCES:
        automata = example['automata']

        for document in example['documents']:
            res_standart = set(map(str, enum_mappings(automata, document)))
            res_naive = set(map(str, naive_enum_mappings(automata, document)))
            assert res_standart == res_naive
