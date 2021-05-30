try:
    from .dev import *  # noqa: F401
except:
    from .prod import *  # noqa: F401