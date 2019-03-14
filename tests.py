import os
import pathlib
import pytest


os.chdir(pathlib.Path.cwd() / 'src/tests')

pytest.main()
