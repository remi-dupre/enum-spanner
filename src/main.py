import dag
import examples


#  A = dag.product_dag(examples.example_1(), 'abaabbba')
#  A.remove_useless_nodes()
#  A.view()

B = dag.product_dag(examples.example_2(), 'a a@b b@a')
B.remove_useless_nodes()
B.view()
