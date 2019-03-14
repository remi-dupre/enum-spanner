import examples
from enum_mappings import enum_mappings, product_dag
from mapping import print_mapping


for example in examples.INSTANCES:
    name = example['name']
    automata = example['automata']


    for num, document in enumerate(example['documents']):
        # Render the output DAG
        dag = product_dag(automata, document)
        dag.remove_useless_nodes()
        dag.render(f'figures/{name}_{num}')

        # Print results
        print('-' * 30)
        print(f'Running {name} over `{document}` ({num})')
        print('-' * 30)

        for mapping in enum_mappings(automata, document):
            print_mapping(document, mapping)
