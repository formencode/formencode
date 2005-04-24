"""
A trivial replacement of PyProtocols
"""

def adapt(obj, protocol):
    return obj

def advise(**kw):
    pass

class Interface(object):
    pass

class Attribute(object):
    def __init__(self, doc, name=None):
        self.doc = doc
        self.name = name

class AdaptationFailure(Exception):
    pass
