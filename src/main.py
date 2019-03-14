import dag
import examples
from enum_mappings import enum_mappings
from naive import naive_enum_matchings


A = dag.product_dag(examples.example_1(), 'abaabbba')
A.remove_useless_nodes()
#  A.view()

B = dag.product_dag(examples.example_2(), 'a a@b b@a')
B.remove_useless_nodes()
#  B.view()

C = dag.product_dag(examples.example_3(), 'aaaaa')
C.remove_useless_nodes()
#  C.view()

for x in enum_mappings(C, [C.initial], []):
    print(x)

print('naive:')
for x in naive_enum_matchings(examples.example_3(), 'aaaaa'):
    print(x)
