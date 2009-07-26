"""
Verify a class implements an interface.
Otherwise return a Null object in its place.
"""

class Null(object):
    def __init__(self, *args, **kwargs): pass
    def __call__(self, *args, **kwargs): pass
    def __repr__(self): return "Null()"
    def __nonzero__(self): return False
    def __getattr__(self, name): return self
    def __setattr__(self, name, value): return self
    def __delattr__(self, name): return self

class InterfaceChecker(type):
    """
    Verifies all required methods are defined or returns Null class in place
    of original class.
    """

    def __new__(mcl, name, bases, d):
        for required_method in d['interface']:
            try:
                d[required_method]
            except KeyError:
                return Null
        return super(InterfaceChecker1, mcl).__new__(mcl, name, bases, d)

