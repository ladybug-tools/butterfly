try:
    from Grasshopper.Kernel.Types import GH_ObjectWrapper as goo
except ImportError:
    pass


def ghWrapper(objs):
    """Put item in a Grasshopper Object Wrapper."""
    try:
        return (goo(obj) for obj in objs)
    except Exception as e:
        raise Exception(
            'Failed to wrap butterfly object in Grasshopper wrapper:\n\t{}'.format(e))
