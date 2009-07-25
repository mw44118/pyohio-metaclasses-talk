==========================+
Clever Uses for Metaclasses
==========================+

**slides are for MBAs**

Really simple metaclass example
===============================

Programmers fight about camelCase (boo!) versus under_score (yay!)
naming conventions.

So I made a metaclass that creates aliases for all methods in a class.

In use
======

>>> from listing1 import peace_between_factions
>>> class C(object):                                                                        
...     __metaclass__ = peace_between_factions                                              
...     def splitLog(self, s):                                                              
...         return s.split(' ')                                                             
...                                                                                         
cls is <class 'C'>                                                                          
name is C                                                                                   
bases are <type 'object'>                                                                   
sorted(d.keys()) are ['__doc__', '__metaclass__', '__module__', 'splitLog'] 
>>> id(c1.split_log) == id(c1.splitLog)
True

The code
========

    class peace_between_factions(type):

        def __init__(cls, name, bases, d):
            super(peace_between_factions, cls).__init__(name, bases, d)

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

*   The print statements show up immediately after the class is defined.
    In other words,  the metaclass __init__ fires once I finished
    defining C.

*   The d parameter maps method names to methods.  The aliasing trick is
simple.  I just conver


Another simple example
=======================

A class wants references to its instances, but not instances of its
subclasses.

This is half right
==================

    >>> class Circle(object):
    ...     instances = []
    ...     def __init__(self):
    ...         self.instances.append(self)
    >>> c1 = Circle()
    >>> c1 in Circle.instances
    True

But is too greedy
=================

    >>> class Ellipse(Circle):
    ...     pass
    >>> e1 = Ellipse()
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

What's the point
================

Never mind the theory.  Metaclasses are just useful ways of minimizing
boilerplate code, just like for loops.

Subclasses vs instances
=======================

    ========== ========== ========
    metaclass  class      instance 
    ========== ========== ========
    type       object     ...
    MC         Shape      s1
    MC         Circle     c1
    MC2        Ellipsis
    ========== ========== ========

Shape has a different metaclass (MC) than object.  Shape's metaclass must be a
subclass of object's metaclass.

Django's ORM
============

    from django.db import models

    class Employee(models.Model):
        login = models.TextField()
        display_name = models.TextField()

    class Department(models.Model):
        name = models.TextField()
        employees = models.ManyToManyField(Employee)

Just based on the definition above, the employees attribute on the
Department class doesn't have a reference to the Department class.

The metaclass handles that part.

In action
=========

    $ python manage.py shell
    In [1]: from scratch.models import Employee, \
    ...     Department
    In [2]: homer = Employee(login="hs",
    ...:                     display_name="H. Simpson")
    In [3]: sector7G = Department(name="Sector 7G")
    In [4]: homer.save()
    In [5]: sector7G.save()
    In [6]: sector7G.employees.all()
    Out[6]: []
    In [7]: sector7G.employees.add(homer)
    In [8]: sector7G.employees.all()
    Out[8]: [<Employee: Employee object>]
    In [9]: _8[0].display_name
    Out[9]: u'H. Simpson'

Where is the magic?
===================

Line 8 shows all employees working in sector 7-G.  That query requires
the department ID for sector 7-G, but the employees attribute has no
obvious reference to the instance it belongs to, so how does it get that
ID?

How does it do that?
====================

1.  The Employee and Department class both descend from
    django.db.models.Model, which has a metaclass named ModelBase.

2.  The models.ManyToManyField class has a method called
    "contribute_to_class".

3.  When Department is instantiated, the ModelBase __new__ method
    executes.  It iterates through all the attributes of Department.
    The metaclass checks each attribute of Department and checks each
    attribute for the existence of a contribute_to_class method.

4.  When it finds contribute_to_class, it calls that method and passes
    in a pointer to Department class and the name 'employees'.  So in
    this case, the employees attribute on the Department class has a
    pointer back to the Department class named 'employees'.


Introducing Crude ORM
=====================

First we'll model these relationships:
        
- Each department has many employees.
- Each employee belongs to exactly one department.
        
This code does the job:

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
    Assigning the colname to department on attribute employees of cls
    Department

The CrudeTable class
====================

    class CrudeTable(object):
        __metaclass__ = MC

        def __init__(self):
            self._id = self.id_ticker.next()

And the MC metaclass
====================

    class MC(type):

        def __init__(cls, name, bases, d):
            super(MC, cls).__init__(name, bases, d)
            
            cls.sqltablename = name.lower()
            cls.id_ticker = count(1) # This is our fake PK.

            for attrname, attr in d.iteritems():

                if hasattr(attr, 'colname'):
                    print ("Assigning the colname to %s on attribute %s of cls %s"
                           % (cls.sqltablename, attrname, name))
                    attr.colname = cls.sqltablename
                    setattr(cls, attrname, property(attr.query))

                if hasattr(attr, 'jointable'):
                    attr.jointable = ("%s_%s" 
                        % (attr.table.sqltablename, cls.sqltablename))

Example usage
=============

    >>> produce = Department("Produce")
    >>> matt = Employee("Matt", produce)
    >>> produce._id
    1
    >>> produce.employees
    'select * from employee where department_id = 1'
    >>> bakery = Department("Bakery")
    >>> lindsey = Employee("Lindsey", bakery)
    >>> charlie = Employee("Charlie", bakery)
    >>> bakery._id
    2
    >>> bakery.employees
    'select * from employee where department_id = 2'

How it works
============

Need three things to get all employees in a department:

* The table to query (employee)
* the column name to test (department_id)
* the value to test for (1 in this case).

By making employees.query into a property named employees, I'm taking
advantage of the fact that employees will get called with self as the
first parameter.


Many-to-many
============

- Each shift requires many employees.
- Each employee works many different shifts.

Example usage
=============

>>> class Shift(CrudeTable):
...
...     def __init__(self, name):
...         super(Shift, self).__init__()
...         self.name = name
...
...     employees = ManyToMany(Employee)
...
Assigning the colname to shift on attribute employees of cls Shift
>>> wednesday_night = Shift("Wednesday Night")
>>> print wednesday_night.employees
select * from employee, employee_shift
where employee.id = employee_shift.employee_id
and employee_shift.shift_id = 1

Explained
=========

The ManyToMany class also needs the name of the table joining the two
other tables.  The MC metaclass watches for attributes with a jointable
attribute, and it fills that in when it finds it.

Cleverness reconsidered
=======================

This shows up a lot::

    Metaclasses are deeper magic than 99% of users should ever worry
    about. If you wonder whether you need them, you don't (the people
    who actually need them know with certainty that they need them, and
    don't need an explanation about why). -- Python Guru Tim Peters


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
    ...

But...
======

*   Decorating a class doesn't decorate subclasses

*   That __contains__ trick isn't possible, because that has to be defined on
    the metaclass.
