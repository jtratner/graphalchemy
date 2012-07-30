
def simple_decorator(decorator):
    """Converts simple functions into well-behaved decorators. (meaning
    that they maintain name, dict, and doc string).
    Heavily based on decorators in Python Decorator Library, but
    modified.
    Example usage::

        @simple_decorator
        def my_decorator(..):
            pass

    INPUT:
        decorator - a decorator function
    OUTPUT:
        the decorator decorated such that it preserves the metadata of the
        functions it decorates
    RAISES:
        ValueError (if decorator function does not return a function)
        """
    # maintain args and kwargs here so that this can work for decorator
    # factories as well
    def new_decorator(f,*args,**kwargs):
        try:
            g = decorator(f,*args,**kwargs)
            g.__name__ = f.__name__
            g.__doc__ = f.__doc__
            g.__module__ = f.__module__
            g.__dict__.update(f.__dict__)
        except AttributeError as e:
            if 'NoneType' in e.message:
                raise ValueError("simple_decorator: decorator must return a function.")
            else:
                raise
        return g
    new_decorator.__name__ = decorator.__name__
    new_decorator.__doc__ = decorator.__doc__
    # not sure here if better to set equal to old dict or update. I
    # guess this format better saves methods from original function
    new_decorator.__dict__.update(decorator.__dict__)
    new_decorator.__module__ = decorator.__module__
    return new_decorator
