from dag import DAG, EmptyLangage
from enum_mappings.explore_dag import enum_dag_mappings
from enum_mappings.precompute_dag import IndexedDag
from enum_mappings.naive import naive_enum_mappings
from mapping import match_of_mapping
from va import VA


def compile_matches(va: VA, text: str) -> DAG:
    '''
    Compile the list of matches of a va over a text into a DAG.
    '''
    #  dag = product_dag(va, text)
    #  dag.remove_useless_nodes(check_accessible=False)
    #  return dag
    return NotImplemented

def enum_mappings(va: VA, text: str):
    dag = IndexedDag(va, text)

    #  for source, target in dag.reach:
    #      print(f'============ {source} -> {target}')
    #      print(f'{source}: {dag.levelset.vertices[source]}')
    #      print(f'{target}: {dag.levelset.vertices[target]}')
    #      print(dag.reach[source, target])

    return enum_dag_mappings(dag)

def enum_matches(va: VA, text: str):
    for mapping in enum_mappings(va, text):
        match = match_of_mapping(text, va.variables, mapping)

        if match.span[0] is not None and match.span[1] is not None:
            yield match
