Constant-Delay Enumeration for Nondeterministic Document Spanners
=================================================================

This is an implementation of the algorithm submitted by Amarilli, Bourhis,
Mengel and Niewerth at [ICDT, 2019](https://arxiv.org/abs/1807.09320) for
Constant-Delay Enumeration for Nondeterministic Document Spanners


Usage
-----

```bash
# Execute current main task (still has a versatile definition)
python3 src/main.py

# Run unit tests
make tests
```

Running the main task will currently output the list of mappings processed
other the examples, and render DAGs that were used in *figures/*.


Dependancies
------------

Dependancies are specified in `requirements.txt`, you can install them manually
or install a virtualenv:

```bash
python -m venv .venv
source .venv/bin/activate  # run this at any time you restarted a shell
pip install -U -r requirements.txt
```
