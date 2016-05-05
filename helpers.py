from importlib import import_module

import config


def to_multiline(t, max_line_length=80):
    start = 0
    while start < len(t):
        stop = min(start + max_line_length, len(t))
        yield t[start:stop]
        start = stop


def replace_config(module):
    if module is None:
        return
    module = import_module(module)
    for name, val in module.__dict__.items():
        setattr(config, name, val)
