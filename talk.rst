==========================+
Clever Uses for Metaclasses
==========================+

Camel-casers and underscorers
=============================

Create aliases for all methods in a class.


Use MCs to tweak subclasses
===========================

A class wants references to its instances
=========================================

    >>> class Circle(object):
    ...     instances = []
    ...     def __init__(self):
    ...         self.instances.append(self)
    >>> c1 = Circle
    >>> c1 in Circle.instances

But not instances of subclasses
===============================

    >>> class Ellipse(Circle):
    ...     pass
    >>> e1 in Circle.instances # YUCK
    True
    >>> id(Ellipse.instances) == id(Circle.instances)
    True

Ghetto solution
===============

    >>> class Ellipse(Circle):
    ...     instances = []
    >>> id(Ellipse.instances) == id(Circle.instances)
    False

Or use a metaclass
==================

    >>> class MC(type):
    ...     def __init__(cls, name, bases, d):
    ...         super(MCCircle, cls).__init__(name, bases, d)
    ...         cls.instances = []

Now redefine the classes
========================

    >>> class Circle(object):
    ...     __metaclass__ = MC
    ...     def __init__(self):
    ...         self.instances.append(self)

    >>> class Ellipse(Circle):
    ...     pass

In action
=========

    >>> c1, c2 = Circle(), Circle()
    >>> c1 in Circle.instances
    True
    >>> e1 = Ellipse()
    >>> e1 in Ellipse.instances
    True
    >>> e1 in Circle.instances
    False

Add a __contains__ method to MC
===============================

    >>> class MC(type):
    ...         def __init__(cls, name, bases, d):
    ...             super(MC, cls).__init__(name, bases, d)
    ...         cls.instances = []
    ... 
    >>>     def __contains__(cls, item):
    ...             return item in cls.instances

Now membership is simpler
=========================

    >>> c1 in Circle
    True

Cookie cutters 
==============

Cookie cutters make cookies.  If you alter the cookie cutter, you alter the
cookie that it makes.  

Big metal presses make cookie cutters.  An altered press makes an altered
cookie cutter, which then makes an altered cookie.

Subclasses vs instances
=======================

    ========== ========== ========
    metaclass  class      instance 
    ========== ========== ========
    type       object     ...
    MC         Shape      s1
    MC         Circle     c1
    ========== ========== ========

Shape has a different metaclass (MC) than object.  Shape's metaclass must be a
subclass of object's metaclass.

A really, really, really simple ORM
===================================




Metaclasses vs class decorators
===============================

Class decorators also allow post-definition, pre-instantiation tweaking. The
camel-case aliasing example is easy::

    >>> from inspect import getmembers, ismethod
    >>> from listing1 import mk_alias
    >>> def aliasmaker(C):
    ...     for name, value in getmembers(C, ismethod):
    ...         setattr(C, mk_alias(name), value)
    ...     return C
    ...
    >>> @aliasmaker
    ... class C(object):
    ...     def split_log(self, s):
    ...         return s.split(' ')
    ...
    >>> c1 = C()
    >>> id(c1.split_log) == id(c1.splitLog)
    True

But class decorators are not hereditary, so you won't get any aliases on
subclasses.
