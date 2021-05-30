# flake8: noqa: F401, F405
try:
    from .dev import *
except:
    from .prod import *