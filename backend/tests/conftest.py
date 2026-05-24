import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault("CONFIG_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "config"))
