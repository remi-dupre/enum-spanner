SRC_DIR=src

.PHONY: test

test:
	PYTHONPATH=$(PWD)/$(SRC_DIR) py.test-3 -vv

