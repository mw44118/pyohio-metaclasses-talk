+++++++++++++++++++++++++++
Clever Uses for Metaclasses
+++++++++++++++++++++++++++

Example: camel-casers and underscorers
======================================

Create underscore-named aliases for all methods in a class.


Example: use MCs to tweak subclasses
====================================

The class wants references to its instances::

    >>> class Circle(object):
    ...     instances = []
    ...     def __init__(self):
    ...         self.instances.append(self)
    ... 
    >>> c1, c2 = Circle(), Circle()
    >>> c1 in Circle.instances and c2 in Circle.instances
    True

But the class doesn't want instances of subclasses::

    >>> class Ellipse(Circle):
    ...     pass
    >>> id(Ellipse.instances) == id(Circle.instances)
    True
    >>> e1 in Circle.instances
    True

Ghetto solution::

    >>> class Ellipse(Circle):
    ...     instances = []
    ... 
    >>> id(Ellipse.instances) == id(Circle.instances)
    False

Do the work in a metaclass instead::

    >>> class MCCircle(type):
    ...     def __init__(cls, name, bases, d):
    ...         super(MCCircle, cls).__init__(name, bases, d)
    ...         cls.instances = []

Now redefine the classes::

    >>> class Circle(object):
    ...     __metaclass__ = MCCircle
    ...     def __init__(self):
    ...         self.instances.append(self)

    >>> class Ellipse(Circle):
    ...     pass

Here it is in action::

    >>> c1, c2 = Circle(), Circle()
    >>> c1 in Circle.instances
    True
    >>> e1 = Ellipse()
    >>> e1 in Ellipse.instances
    True
    >>> e1 in Circle.instances
    False







Some boring theory
==================

Cookie cutter metaphor
----------------------

Cookie cutters make cookies.  If you alter the cookie cutter, you alter
the cookie that it makes.  

Big metal presses make cookie cutters.  An altered press makes an
altered cookie cutter, which then makes an altered cookie.


Subclasses vs instances
-----------------------

A really, really simple ORM
===========================




Metaclasses vs class decorators
===============================

The camel-case vs underscore example would easily work as a class
decorator.

The rocking chair example would not be easy because class decorators
are not hereditary!


Something much simpler and almost as powerful: prototypes
=========================================================



