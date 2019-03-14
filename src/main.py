import dag
import examples


A = dag.product_dag(examples.example_1(), 'aa')
print(A)
A.remove_useless_nodes()
print(A)
