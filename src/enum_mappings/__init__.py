from enum_mappings.explore_dag import enum_dag_mappings
from enum_mappings.precompute_dag import product_dag
from enum_mappings.naive import naive_enum_mappings
from va import VA


def enum_mappings(va: VA, text: str):
    dag = product_dag(va, text)
    dag.remove_useless_nodes()
    yield from enum_dag_mappings(dag)
