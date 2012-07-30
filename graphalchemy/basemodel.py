
class BaseNode(object):
    """ABC-ish Node representation for SQLAlchemy nodes.

    Has the following attributes:

        :param id: primary key
        :type id: int (need not be specified)
        :param size: size of node
        :type size: int
        :param label: label for the node
        :type label: unicode
        :param color: node color
        :type color: unicode (10 characters)

    Also has relationship to BaseEdge via:

        :attr:`in_edges` - edges where BaseNode is target
        :attr:`out_edges` - edges where BaseNode is source

    Does NOT define `__init__`"""
    COLORLENGTH=10
    attrs = frozenset(["size", "label", "color"])

    @classmethod
    def create(cls, obj=None, attrs=None, id=None, **kwargs):
        """ creates an instance of class, given an object and the
        attributes to take from it. (if attrs is None, tries to get
        cls.attrs next. If an attribute is not on object,
        stores None instead.
        kwargs are passed through, but are overwritten by attributes
        on object if in `attrs`.

        If obj is None, just creates with kwargs.
        Note that id is a primary key, so be careful with passing it!"""
        attrs = attrs or cls.attrs
        if object:
            for k in attrs:
                v = getattr(obj, k, None)
                if v is not None:
                    kwargs[k] = v
        return cls(id=id, **kwargs)

    @property
    def edges(self):
        """ returns both in and out edges (starts with in then out)"""
        return self.in_edges + self.out_edges

    def iter_edge_targets(self, node=None):
        """ *generator that returns tuples of (edge, other_node)

        if node is passed, will use node for in_edges and out_edges,
            this (should?) let you specify a queried node and change the join
            attributes on it just for this query

        Parameters:
            :param node: an instance of a class deriving from BaseNode (optional)
        """

        node = node or self

        for edge in node.in_edges:
            yield edge, edge.source

        for edge in node.out_edges:
            yield edge, edge.target

    @property
    def neighbors(self):
        """ returns a generator for the neighbors of the node,
        uses iter_edge_targets to find neighbors """
        for edge, node in self.iter_edge_targets():
            yield node

    def __repr__(self):
        return "<{cls}({vals})>".format(cls=self.__class__.__name__,
                vals=repr([(k,getattr(self,k,None)) for k in self.attrs]))

class BaseEdge(object):
    """ABC edge representation for graphalchemy edges.
    Only source, target are required (or source_id, target_id required).
    Has the following parameters:

       :param id: primary key
       :type id: int
       :param size: size of edge
       :type size: float
       :param label: label of edge (e.g. for display)
       :type label: unicode
       :param weight: the edge-weight
       :type weight: float
       :param color: color of edge
       :type color: unicode (10 characters)

    References to BaseNodes:

        :param source_id: foreignkey to BaseNode - REQUIRED!
        :type target_id: int
        :param target_id: foreignkey to TargetNode - REQUIRED!
        :type target_id: int
        :param source: - relationship/actual node that is the source of edge
        :type source: :class:`BaseNode` or (`BaseNode`-equivalent type)
        :param target: relationship/actual node that is target of edge
        :type target: :class:`BaseNode` or (`BaseNode` equivalent type)

    `__getitem__`, `__setitem__`:

        :meth:`__getitem__` returns id of source/target
            (so can use *edge operator with networkx, w/o maintaining refs)
        :meth:`__setitem__` must set with BaseNode instance OR with id

    Does NOT define `__init__`
    """
    COLORLENGTH = 10
    def __getitem__(self, n):
        if n in (0, -1):
            return self.source_id
        elif n in (1, -2):
            return self.target_id
        else:
            raise IndexError("Only has source, target node. '%d' is out of range" % n)

    def __setitem__(self, n, node):
        if not isinstance(node, BaseNode):
            raise TypeError("Only instances of BaseNode can be set as source and target")
        if n in (0, -1):
            self.source = node
            self.source_id = node.id
        elif n in (1, -2):
            self.target = node
            self.target_id = node.id
        else:
            raise IndexError("Node assignment out of range. Only has source, target node. '%d' is out of range" % n)
    attrs = frozenset(["size", "label", "weight", "directed",
        "source_id", "target_id", "source", "target"])
    @classmethod
    def create(cls, obj=None, attrs=None, id=None, **kwargs):
        """ creates an instance of class, given an object and the
        attributes to take from it. (if attrs is None, tries to get
        cls.attrs next. If an attribute is not on object,
        stores None instead.
        kwargs are passed through, but are overwritten by attributes
        on object if in `attrs`.

        If obj is None, just creates with kwargs.
        Note that id is a primary key, so be careful with passing it!"""
        attrs = attrs or cls.attrs
        if object:
            for k in attrs:
                v = getattr(obj, k, None)
                if v is not None:
                    kwargs[k] = v
        return cls(id=id, **kwargs)

    @classmethod
    def connect_nodes(cls, source=None, target=None, **kwargs):
        """ Connect source and target by creating an edge.
        `kwargs` are passed to the `cls` constructor. 
        Only need to pass source, target or source_id, target_id """
        edge = cls(**kwargs)
        if source:
            edge.source = source
        if target:
            edge.target = target
        return edge
    def __repr__(self):
        return "<{cls}({vals})>".format(cls=self.__class__.__name__,
                vals=repr([(k,getattr(self,k,None)) for k in self.attrs]))

