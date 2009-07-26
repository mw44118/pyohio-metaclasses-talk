# listing1.py

"""
Define metaclasses that create function aliases from one naming convention to
another.
"""

import types

def cc2us(s):
    """
    Translate string s from its camel-case format to underscores.

    >>> cc2us('ILoveCamelCase')
    'I_love_camel_case'

    >>> cc2us('FirstPrize')
    'First_prize'
    """

    outstring = ""
    for i, c in enumerate(s):
        if i > 0 and c.isupper(): 
            outstring += "_%c" % c.lower()
        else: outstring += c
    return outstring


def us2cc(s):
    """
    Translate string s from underscores to camel-case.

    >>> us2cc("first_prize")
    'firstPrize'

    >>> us2cc("I_love_camel_case")
    'ILoveCamelCase'
    """

    outstring = str()
    should_call_upper_on_next_letter = False
    for c in s:
        if c == "_": 
            should_call_upper_on_next_letter = True
        else:
            if should_call_upper_on_next_letter:
                d = c.upper()
                should_call_upper_on_next_letter = False
            else:
                d = c
            outstring += d
    return outstring

def mk_alias(s):
    """
    Return a camel-cased version of string s IFF s is an underscored string.
    Return an underscored version of string s IFF s is camel-case.

    >>> mk_alias('log_parse')
    'logParse'

    >>> mk_alias('logParse')
    'log_parse'
    """

    cc = us2cc(s)

    # If converting the string to camel-case didn't alter it, return an
    # underscored version.
    if cc == s:
        return cc2us(s)
    
    else:
        return cc

class peace_between_factions(type):

    def __init__(cls, name, bases, d):
        super(peace_between_factions, cls).__init__(name, bases, d)

        # Some instructive print statements
        print "cls is %s" % cls
        print "name is %s" % name
        print "bases are %s" % bases
        # print "d is %s" % d

        # Iterate through each attribute in the class.

        for attrname, attr in d.items():

            # For methods, create an alias.
            if type(attr) in (types.FunctionType, types.MethodType):
                setattr(cls, mk_alias(attrname), attr)
