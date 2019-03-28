SRC_DIR=src

.PHONY: test

test:
	PYTHONPATH=$(PWD)/$(SRC_DIR) python3 -m pytest -vv

