"""
=======================================
Google App Engine BaseNode and BaseEdge
=======================================

Representation of a `BaseEdge` and a `BaseNode` that will work on Google App
Engine. Has all the same methods as the other implementations of BaseNode and
BaseEdge, including a One-to-Many relationship between BaseEdges and
BaseNodes.

Note that it still uses :meth:`BaseNode.__getitem__`, so it returns `id`s,
not objects.

If you are using `webapp2` or `wertzkreug`, you might want to use the
:meth:`utils.cached_property` method to prevent multiple queries for source
and target; however, it's not clear to the author whether GAE actually makes a
new datastore query for every call to source and target.

.. warning::

    When creating new objects, you should generally make the Nodes first, save
    them, and *then* add the edges. Otherwise, you risk asking for the id/key
    of an object that doesn't yet exist.

    Otherwise, be careful not to call methods that will ask for the id of an
    object before saving (e.g. calling :meth:`GAEBaseEdge.source_id` before
    the source node has been saved)

"""
from basemodels import BaseNode, BaseEdge
from google.appengine.ext.db import (
        PolyModel,
        ReferenceProperty,
        FloatProperty,
        BooleanProperty,
        StringProperty,
        )
class GAEBaseNode(BaseNode, PolyModel):
    """
    A :class:`db.PolyModel` (basically, a superclass for any descending Node model).
    Will query references to edges using the :class:`GAEBaseEdge` PolyModel,
    which means that asking for `in_edges` and `out_edges` will result in query
    results for *all* subclasses of :class:`GAEBaseEdge` that reference :class:`GAEBaseNode`

    If you want it to be more specific, just subclass :class:`GAEBaseNode`
    """
    attrs = frozenset(["size", "label", "color"])

    @property
    def id(self):
        """ id of the key of the current instance """
        return self.key().id()

    label = StringProperty()
    color = StringProperty()
    size = FloatProperty()


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
    @property
    def in_edges(self):
        """ generator `GQL` query that returns all edges that target
        this :class:`GAEBaseNode`

        NOTE: this still needs to be tested on GAE, not sure whether this is
        legal.
        """
        return GAEBaseEdge.gql("WHERE target :1", self)

    @property
    def out_edges(self):
        """ generator `GQL` query that returns all edges that derive
        this :class:`GAEBaseNode`"""

        return GAEBaseEdge.gql("WHERE source :1", self)

    def __repr__(self):
        return "<{cls}({vals})>".format(cls=self.__class__.__name__,
                vals=repr([(k,getattr(self,k,None)) for k in self.attrs]))

class GAEBaseEdge(BaseEdge, PolyModel):
    """
    A :class:`db.PolyModel` (basically, a superclass for any inheriting Edge model).

    If you want it to be more specific, just subclass :class:`GAEBaseNode`

    If you query on this class, you can potentially get results from *all* descendants
    of :class:`GAEBaseEdge`
    """
    @property
    def id(self):
        """ the id of the key of the current instance """
        return self.key().id()

    size = FloatProperty()
    label = StringProperty()
    weight = FloatProperty()
    color = StringProperty()
    directed = BooleanProperty()
    source = ReferenceProperty(reference_class="GAEBaseNode", collection_name="GAEBaseNode_source_set")
    target = ReferenceProperty(reference_class="GAEBaseNode", collection_name="GAEBaseNode_target_set")

    @property
    def source_id(self):
        """ returns the `id` of the :class:`db.Key` stored in
        :attr:`source`. (keeps it compatible with the interfaces
        for the other :mod:`graphalchemy` classes"""
        return self.source.id

    @property
    def target_id(self):
        """ returns the `id` of the :class:`db.Key` stored in
        :attr:`target`. (keeps it compatible with the interfaces
        for the other :mod:`graphalchemy` classes"""
        return self.target.id

    def __setitem__(self, n, node):
        """ GAEBaseNode needs to store only source and target (and would raise
        an error if tried to get source_id or target_id)"""
        if isinstance(node, BaseNode):
            raise TypeError("Only instances of BaseNode can be set as source and target")
        if n in (0, -1):
            self.source = node
        elif n in (1, -2):
            self.target = node
        else:
            raise IndexError("Node assignment out of range. Only has source, target node. '%d' is out of range" % n)
    def __repr__(self):
        return "<{cls}({vals})>".format(cls=self.__class__.__name__,
                vals=repr([(k,getattr(self,k,None)) for k in self.attrs]))
    def __str__(self):
        return "({src}, {tgt})".format(src=self.source_id, tgt=self.target_id)

