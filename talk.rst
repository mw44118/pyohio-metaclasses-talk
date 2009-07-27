===========================
Clever Uses for Metaclasses
===========================


Really simple metaclass example
===============================

Programmers fight about camelCase (boo!) versus under_score
(yay!) naming conventions.

So I made a metaclass that creates aliases from each
convention to the other.


In use
======

::

    >>> from listing1 import peace_between_factions
    >>> class C(object):
    ...     __metaclass__ = peace_between_factions
    ...     def splitLog(self, s):
    ...         return s.split(' ')
    ...
    cls is <class 'C'>
    name is C
    bases are <type 'object'>
    >>> c1 = C()
    >>> id(c1.split_log) == id(c1.splitLog)
    True


The code
========

First I wrote a silly function::

    >>> from listing1 import mk_alias
    >>> mk_alias('under_score')
    'underScore'
    >>> mk_alias('camelCase')
    'camel_case'

Then I wrote this metaclass::

    class peace_between_factions(type):

        def __init__(cls, name, bases, d):

            super(peace_between_factions, cls)\
            .__init__(name, bases, d)

            # Some instructive print statements
            print "cls is %s" % cls
            print "name is %s" % name
            print "bases are %s" % bases
            print "sorted(d.keys()) are %s" % sorted(d.keys())

            for attrname in d:
                attr = getattr(cls, attrname)
                # For methods, create an alias.
                if type(attr) == types.MethodType:
                    setattr(cls, mk_alias(attrname), attr)

Stuff to notice
===============

*   The print statements show up immediately after the class
    is defined.  In other words,  the metaclass __init__
    fires once I finished defining C.

*   The d parameter holds everything in the class definition.


Another simple example
======================

A class wants references to its instances, but not instances
of its subclasses.

This is half right
==================

::

    >>> class Circle(object):
    ...     instances = []
    ...     def __init__(self):
    ...         self.instances.append(self)
    >>> c1 = Circle()
    >>> c1 in Circle.instances
    True

But is too greedy
=================

::

    >>> class Ellipse(Circle):
    ...     pass
    >>> e1 = Ellipse()
    >>> e1 in Circle.instances # YUCK
    True
    >>> id(Ellipse.instances) == id(Circle.instances)
    True

Ghetto solution
===============

::

    >>> class Ellipse(Circle):
    ...     instances = []
    >>> id(Ellipse.instances) == id(Circle.instances)
    False

*   I'll probably forget to manually add it.
*   It sure is repetitive.


Or use a metaclass
==================

::

    >>> class MC(type):
    ...     def __init__(cls, name, bases, d):
    ...         super(MC, cls).__init__(name, bases, d)
    ...         cls.instances = []


Now redefine the classes
========================

::

    >>> class Circle(object):
    ...     __metaclass__ = MC
    ...     def __init__(self):
    ...         self.instances.append(self)

    >>> class Ellipse(Circle):
    ...     pass


In action
=========

::

    >>> c1, c2 = Circle(), Circle()
    >>> c1 in Circle.instances
    True
    >>> e1 = Ellipse()
    >>> e1 in Ellipse.instances
    True
    >>> e1 in Circle.instances
    False


Add a __contains__ method
=========================

This would be prettier::

    c1 in Circle

This ain't gonna work::

    >>> class C(object):
    ...     instances = []
    ...     def __init__(self):
    ...         self.instances.append(self)
    ...     @classmethod
    ...     def __contains__(cls, item):
    ...         return item in cls.instances
    ... 
    >>> c1 = C()
    >>> c1 in C
    Traceback (most recent call last):
    ...
    TypeError: argument of type 'type' is not iterable


Add __contains__ to the metaclass
=================================

::

    >>> class MC2(type):
    ...     def __init__(cls, name, bases, d):
    ...         super(MC2, cls).__init__(name, bases, d)
    ...         cls.instances = []
    ...     def __contains__(cls, item):
    ...             return item in cls.instances

Demonstration
=============

::

    >>> class C(object):
    ...     __metaclass__ = MC2
    ...     def __init__(self):
    ...         self.instances.append(self)
    ... 
    >>> c1 = C()
    >>> c1 in C # Uses MC2's __contains__ method
    True


Cookie cutters 
==============

Cookie cutters make cookies.  Round cutters make round
cookies and square cutters make square cookies.

Big metal machine presses make cookie cutters.  An altered
press makes an altered cookie cutter, which then makes an
altered cookie.


Subclasses vs instances
=======================

    =============== ======= ===========
    metaclass       class   instance 
    =============== ======= ===========
    type            object    ...
    MC              C         c1
    =============== ======= ===========


Since C subclasses object, C's metaclass must be the same as
object's metaclass OR C's metaclass must be a subclass of
object's metaclass.


__new__ vs __init__
===================

__new__ has to make the class and then return it.  __init__
just has to dress it up.  

You can use __new__ to prevent a class to be defined or even
replace it with another class.


Verify an interface
===================

Use a metaclass to check that a class class defines all
expected methods.  If not, the __new__ method will replace
the class with a Null class::

    >>> from listing2 import InterfaceChecker
    >>> rocketship = ['launch'] # this is my interface
    >>> class Soyuz(object):
    ...     __metaclass__ = InterfaceChecker
    ...     interface = rocketship
    ...
    >>> s1 = Soyuz()
    >>> type(s1)
    <class 'listing2.Null'>


The metaclass responsible
=========================

::

    class InterfaceChecker(type):

        def __new__(mcl, name, bases, d):
            for required_method in d['interface']:
                try:
                    d[required_method]
                except KeyError:
                    return Null

            return super(InterfaceChecker1, mcl).\
            __new__(mcl, name, bases, d)


Introducing Crude ORM
=====================

First we'll model these relationships:
        
*   Each department has many employees.
*   Each employee belongs to exactly one department.

My ORM just returns SQL strings.


Example usage
=============

::

    >>> from listing4 import *
    >>> produce = Department("Produce")
    >>> matt = Employee("Matt", produce)
    >>> produce._id
    1
    >>> produce.employees
    'select * from employee where department_id = 1'

How does the employees attribute know that produce has an
_id of 1?


The Employee and Department classes
===================================
        
::

    >>> from listing4 import *
    >>> class Employee(CrudeTable):
    ...
    ...     def __init__(self, name, department):
    ...         super(Employee, self).__init__()
    ...         self.name = name 
    ...         self.department = department
    ...     
    >>> class Department(CrudeTable):
    ...     
    ...     def __init__(self, name):
    ...         super(Department, self).__init__()
    ...         self.name = name
    ...         
    ...     employees = OneToMany(Employee)


The CrudeTable class
====================

::

    class CrudeTable(object):
        __metaclass__ = MC

        def __init__(self):
            self._id = self.id_ticker.next()


And the MC metaclass
====================

::

    class MC(type):

        def __init__(cls, name, bases, d):
            super(MC, cls).__init__(name, bases, d)
            
            cls.sqltablename = name.lower()
            cls.id_ticker = count(1) # This is our fake PK.

            for attrname, attr in d.iteritems():

                if hasattr(attr, 'colname'):
                    attr.colname = cls.sqltablename
                    setattr(cls, attrname, property(attr.query))

                if hasattr(attr, 'jointable'):
                    attr.jointable = "%s_%s"  \
                    % (attr.table.sqltablename, cls.sqltablename))


How it works
============

Need three things to get all employees in a department:

* The table to query (employee)
* the column name to test (department_id)
* the value to test for (1 in this case).

By making employees.query into a property named employees,
I'm taking advantage of the fact that employees will get
called with self as the first parameter.


Many-to-many
============

- Each shift requires many employees.
- Each employee works many different shifts.


Example usage
=============

::

    >>> class Shift(CrudeTable):
    ...
    ...     def __init__(self, name):
    ...         super(Shift, self).__init__()
    ...         self.name = name
    ...
    ...     employees = ManyToMany(Employee)
    ...
    >>> wednesday_night = Shift("Wednesday Night")
    >>> print wednesday_night.employees
    select * from employee, employee_shift
    where employee.id = employee_shift.employee_id
    and employee_shift.shift_id = 1


Explained
=========

The ManyToMany class also needs the name of the table
joining the two other tables.  The MC metaclass watches for
attributes with a jointable attribute, and it fills that in
when it finds it.


Cleverness re-reconsidered
==========================

This shows up a lot::

    Metaclasses are deeper magic than 99% of users should
    ever worry about. If you wonder whether you need them,
    you don't (the people who actually need them know with
    certainty that they need them, and don't need an
    explanation about why). -- Python Guru Tim Peters


Metaclasses vs class decorators
===============================

The camel-case aliasing example is easy::

    >>> from inspect import getmembers, ismethod
    >>> from listing1 import mk_alias
    >>> def aliasmaker(C):
    ...     for name, value in getmembers(C, ismethod):
    ...         setattr(C, mk_alias(name), value)
    ...     return C
    ...
    >>> @aliasmaker
    ... class C(object):
    ...     def splitLog(self, x):
    ...         pass

But...
======

*   Decorating a class doesn't decorate subclasses

*   That __contains__ trick isn't possible, because that has
    to be defined on the metaclass.


Prototypes are the real anti-metaclass
======================================

*   When you ask an object for an attribute or a method it
    doesn't have, it will ask its prototype for it.  
    
*   If the prototype doesn't have it, it will ask its
    prototype.

*   The chain continues until somebody knows what to do or
    we run out of prototypes.


Trivial javascript example
==========================

::

    js> var O = function () {
        this.a = 1;
        this.b = 2;
    };
    js> var o = new O();
    js> o.a
    1
    js> o.c == null
    true

Define a prototype for O
========================

::

    js> var P = function () {
        this.c = 3;
    };
    js> var Q = function () {
        this.d = 4;
    };
    js> P.prototype = new Q();
    [object Object]
    js> O.prototype = new P();
    [object Object]

Now failed lookups on O will go to P, and then to Q.

In action
=========

::

    js> var o = new O();
    js> o.a
    1
    js> o.c // from P.
    3
    js> o.d // from Q.
    4


Now change stuff at runtime
===========================

::

    js> O.prototype = new function () {this.c = 99}()
    [object Object]
    js> var o2 = new O();
    js> o2.c
    99
    js> o.c
    3


Stuff to keep in mind
=====================

*   Forget all about instantiation and subclassing and just
    think about cloning.  After you clone something,
    trashing the original doesn't affect the clone.

*   Classes are really just linked lists of lookup tables
    now, and you can monkey with them at runtime.


Trivial Python implementation
=============================

::

    >>> class ProtoC(object):
    ...     def __getattr__(self, k):
    ...         if self.prototype:
    ...             return getattr(self.prototype, k)
    ...     def __init__(self, **kwargs):
    ...         self.prototype = None
    ...         self.__dict__.update(**kwargs)
    ... 
    >>> c1 = ProtoC(a=1, b=2)
    >>> c2 = ProtoC(prototype=c1)
    >>> c2.a
    1
    >>> c2.a = 11
    >>> c1.a, c2.a
    (1, 11)

Lots more to prototypes
=======================

*   Every object should have a clone method.

*   Should be easy to add methods that reference self at
    runtime.
