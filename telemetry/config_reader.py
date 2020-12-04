import json
from os.path import join, dirname, abspath

CONFIG = abspath(join(dirname(__file__), "config.txt"))


def load_config():
    """Return config as a dictionary."""
    with open(CONFIG) as f:
        config = f.read()
    return json.loads(config)

