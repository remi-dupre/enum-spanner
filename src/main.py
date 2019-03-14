import examples
from enum_mappings import enum_mappings
from mapping import print_mapping


for example in examples.INSTANCES:
    name = example['name']
    automata = example['automata']

    for document in example['documents']:
        print('-' * 30)
        print(f'Running {name} over `{document}`')
        print('-' * 30)

        for mapping in enum_mappings(automata, document):
            print_mapping(document, mapping)


