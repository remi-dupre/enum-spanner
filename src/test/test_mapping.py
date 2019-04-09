import pytest

import examples
from enum_mappings import enum_mappings, naive_enum_mappings


def test_run_example():
    def normalize_mapping(mapping):
        return set(str(sorted(spanner)) for spanner in mapping)

    for example in examples.INSTANCES:
        automata = example['automata']

        for document in example['documents']:
            res_standart = normalize_mapping(enum_mappings(automata, document))
            res_naive = normalize_mapping(naive_enum_mappings(automata, document))
