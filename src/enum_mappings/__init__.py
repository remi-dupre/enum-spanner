from enum_mappings.indexed_dag import IndexedDag
from enum_mappings.jump import EmptyLevel
from enum_mappings.naive import naive_enum_mappings
from mapping import match_of_mapping
from va import VA


def compile_matches(va: VA, text: str) -> IndexedDag:
    '''
    Compile the list of matches of a Variable Automata over a text into a DAG.
    '''
    return IndexedDag(va, text)


def enum_mappings(va: VA, text: str):
    '''
    Iterate over the mappings of the given Variable Automaton over a text.
    '''
    try:
        dag = compile_matches(va, text)
    except EmptyLevel:
        return iter([])

    return iter(dag)


def enum_matches(va: VA, text: str):
    '''
    Iterate over the matches of the given Variable Automaton over a text.
    '''
    for mapping in enum_mappings(va, text):
        match = match_of_mapping(text, va.variables, mapping)

        if match.span[0] is not None and match.span[1] is not None:
            yield match
