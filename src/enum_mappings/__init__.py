from dag import EmptyLangage
from enum_mappings.explore_dag import enum_dag_mappings
from enum_mappings.precompute_dag import product_dag
from enum_mappings.naive import naive_enum_mappings
from mapping import match_of_mapping
from va import VA


def enum_mappings(va: VA, text: str):
    dag = product_dag(va, text)

    try:
        dag.remove_useless_nodes()
    except EmptyLangage:
        return iter([])

    return enum_dag_mappings(dag)

def enum_matches(va: VA, text: str):
    for mapping in enum_mappings(va, text):
        yield match_of_mapping(text, va.variables, mapping)
