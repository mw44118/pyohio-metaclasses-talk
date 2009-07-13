# listing3.py

"""
Vastly simplified example of ORM metaclass trickery.
"""

from itertools import count

class ManyToMany(object):

    def __init__(self, table):
        self.table = table
        self.jointable = None
        self.colname = '%s_id' % table.sqltablename

    def query(self, x):

        d = dict(table=self.table.sqltablename,
                 jointable=self.jointable,
                 colname=self.colname,
                 colvalue=x._id)

        return ("select * from %(table)s, %(jointable)s\n"
                "where %(table)s.id = %(jointable)s.%(table)s_id\n"
                "and %(jointable)s.%(colname)s_id = %(colvalue)s"
                % d)

class OneToMany(object):

    def __init__(self, table):
        self.table = table
        self.colname = None # The metaclass adds this.

    def query(self, x):

        """
        Returns a string like 
        "select * from employee where department_id = 99"
        x must have an _id attribute.
        """

        return ("select * from %s where %s_id = %s" 
                % (self.table.sqltablename, self.colname, x._id))

class MC(type):

    def __init__(cls, name, bases, d):
        super(MC, cls).__init__(name, bases, d)
        
        cls.sqltablename = name.lower()
        cls.id_ticker = count(1) # This is our fake PK.

        for attrname, attr in d.iteritems():

            if hasattr(attr, 'colname'):
                print (
"Assigning the colname to %s on attribute %s of cls %s"
                       % (cls.sqltablename, attrname, name))
                attr.colname = cls.sqltablename
                setattr(cls, attrname, property(attr.query))

            if hasattr(attr, 'jointable'):
                attr.jointable = ("%s_%s" 
                    % (attr.table.sqltablename, cls.sqltablename))
            
class CrudeTable(object):
    __metaclass__ = MC

    def __init__(self):
        self._id = self.id_ticker.next()
