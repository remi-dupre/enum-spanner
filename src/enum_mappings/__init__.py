from dag import DAG, EmptyLangage
from enum_mappings.explore_dag import enum_dag_mappings
from enum_mappings.precompute_dag import product_dag
from enum_mappings.naive import naive_enum_mappings
from mapping import match_of_mapping
from va import VA


def compile_matches(va: VA, text: str) -> DAG:
    '''
    Compile the list of matches of a va over a text into a DAG.
    '''
    dag = product_dag(va, text)
    dag.remove_useless_nodes(check_accessible=False)
    return dag

def enum_mappings(va: VA, text: str):
    try:
        dag = compile_matches(va, text)
    except EmptyLangage:
        return iter([])

    return enum_dag_mappings(dag)

def enum_matches(va: VA, text: str):
    for mapping in enum_mappings(va, text):
        match = match_of_mapping(text, va.variables, mapping)

        if match.span[0] is not None and match.span[1] is not None:
            yield match
