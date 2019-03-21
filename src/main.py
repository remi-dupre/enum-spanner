import compile.build_nfa as build_nfa
from compile.grammar import build_ast
from compile.glushkov import ASTtoNFA


tree = build_ast('a*ba*')
print(tree.pretty())
ASTtoNFA().transform(tree).render('test')


#  import examples
#  from benchmark import bench, random_word, print_tracking
#  from enum_mappings import enum_mappings, naive_enum_mappings
#  from enum_mappings.precompute_dag import product_dag
#  from mapping import print_mapping
#  from va import VA

#  #  Output unit tests results
#  for example in examples.INSTANCES:
#      name = example['name']
#      automata = example['automata']
#
#      automata.render(f'figures/va/{name}')
#
#      for num, document in enumerate(example['documents']):
#          # Render the output DAG
#          dag = product_dag(automata, document)
#          dag.remove_useless_nodes()
#          dag.render(f'figures/dag/{name}.{num}')
#
#          # Print results
#          print('-' * 30)
#          print(f'Running {name} over `{document}` ({name}.{num})')
#          print('-' * 30)
#
#          for mapping in enum_mappings(automata, document):
#              print_mapping(document, mapping)
#
#  # Run benchmarks
#  print('\n----- Run benchmarks')
#
#  automata = examples.example_4()
#  inputs = {
#      'repeat': 'aaaaabbbbb' * 10**4,
#      'random': random_word(10**5, 'ab'),
#      # 'random': random_word(10**5, ' aaaa..@')
#  }
#
#  def naive_algorithm(va: VA):
#      return lambda x: naive_enum_mappings(va, x)
#
#  def standart_algorithm(va: VA):
#      return lambda x: enum_mappings(va, x)
#
#  print('\nBenchmark for standart algorithm')
#  bench(standart_algorithm(automata), inputs)
#
#  print('\nBenchmark for naive algorithm')
#  bench(naive_algorithm(automata), inputs)
#
#  print_tracking()
