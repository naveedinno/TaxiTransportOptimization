from time import time
from functools import wraps


def timer(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print(f"{f.__name__} took {te - ts} second\n")
        return result

    return wrap
