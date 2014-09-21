def inverse_dict(d):
    return {v:k for k, v in d.items()}

def partition(l, n):
    """partitions a list into parts of size n."""
    for i in range(0, len(l), n):
       yield l[i:i+n]
 
def split_seq_query(query, seq, max_size=999):
    """split a large `in` query into several queries"""
    parts = partition(seq, max_size)
    result = []
    for p in parts:
        result += query(p).all()
    return result

class Delegate(object):
    """
    A descriptor based recipe that makes it possible to write shorthands
    that delegates attribute access from one object onto another.

    >>> class C(object):
    ...     def __init__(self):
    ...         class Proxy(object):
    ...             def bar(self):
    ...                 return "bar" 
    ...             foo = 42
    ...         self.proxy = Proxy()
    ...
    ...     bar = forwardTo('proxy', 'bar')
    ...     foo = forwardTo('proxy', 'foo')
    ...
    >>> print C().bar()
    bar
    >>> print C().foo
    42

    Arguments: objectName - name of the attribute containing the second object.
               attrName - name of the attribute in the second object.
    Returns:   An object that will forward any calls as described above.
    """
    def __init__(self, objectName, attrName):
        self.objectName = objectName
        self.attrName = attrName

    def __get__(self, instance, owner=None):
        return getattr(getattr(instance, self.objectName), self.attrName)

    def __set__(self, instance, value):
        print "write access not allowed to delegate object" 
