'''Utils - taken from https://github.com/dlink/vlib'''

class MissingArguments(Exception): pass

def validate_num_args(s, num_args, args):
    if len(args) < num_args:
        pluralization = 's'
        if num_args == 1:
            pluralization = ''
        error_msg = '%s takes %s argument%s.' % (s, num_args, pluralization)

        if not args:
            error_msg += '  None given.'
        else:
            error_msg += '  Only %s given: %s' % (len(args), ", ".join(args))
        raise MissingArguments(error_msg)

def pretty(X):
    '''Return X formated nicely for the console'''
    o = ''
    if isinstance(X, (list, tuple)):
        if X and isinstance(X[0], (list, tuple)):
            for row in X:
                o +=  ",".join(map(str, row)) + '\n'
        else:
            o += "\n".join(map(str, X)) + '\n'
    elif isinstance(X, dict):
        keys = sorted(X.keys())
        for k in keys:
            o +=  "%s: %s" % (k, X[k]) + '\n'
    else:
        o += str(X)
    return o.strip() # strip off final \n so we can print it

def lazyproperty(fn):
    '''A decorator that computes a property variable and then caches.
    http://stackoverflow.com/questions/3012421/python-lazy-property-decorator
    '''
    attr_name = '_lazy_' + fn.__name__
    @property
    def _lazyproperty(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazyproperty
