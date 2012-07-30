"""
Models:

    this module allows the creation of a few base classes to make it easier
    to work with SQLAlchemy in creating (directed/undirected) graphs and edges.

        """
import sqlalchemy.ext.declarative as decl # declared_attr
import sqlalchemy as sqla # Column, Integer, Unicode, Float, Boolean, ForeignKey
import sqlalchemy.orm as orm # relationship, backref
# overwrite a few extensions to use flask-sqlalchemy's model
import os

def sqlite_connect(dbpath, metadata, create_engine=sqla.create_engine,
        sessionmaker=orm.sessionmaker, echo=True):
    """ return an sqllite connection to the given dbpath.
    Optional arguments default to sqlalchemy functions.

    Parameter:
        :param dbpath: path (relative or absolute) to database (unicode/string)
        :param metadata: something that supports create_all(engine) to create/load tables
        :type metadata: should create tables with `create_all(engine)`
        :type create_engine: function (dbpath) -> engine
        :param sessionmaker: (optional) must take `bind=engine`, return a class that can be called
                            to create a session
        :type sessionamker: function (bind=engine) --> Session

    Returns:
       :returns: (engine, session)
    """
    create_engine = create_engine or sqla.create_engine
    sessionmaker = sessionmaker or orm.sessionmaker
    dbpath = os.path.abspath(dbpath)
    engine = create_engine("sqlite:///" + dbpath, echo=echo)
    metadata.create_all(engine)
    session = (sessionmaker(bind=engine))()
    return engine, session

def class_to_tablename(class_str):
    """ converts `class_str` to a tablename, s.t.
    CamelCase --> camel_case """
    def add_underscore(matchobj):
        match = matchobj.group(0)
        return match[0] + "_" + match[1]
    # put an _ between every lowerUpper match, e.g.:
    # "aA" --> "a_A"
    # then convert everything to lower case
    # OR add underscores between double caps.
    import re
    match = re.compile("[a-z][A-Z]|[A-Z][A-Z]")
    # need to do it twice because AAA --> "a_a_a")
    return re.sub(match, add_underscore,
            re.sub(match, add_underscore, class_str)).lower()


def create_base_classes(
        NodeClass,
        EdgeClass,
        NodeTable = None,
        EdgeTable = None,
        declared_attr = decl.declared_attr,
        Column = sqla.Column,
        Integer = sqla.Integer,
        Unicode = sqla.Unicode,
        Float = sqla.Float,
        Boolean = sqla.Boolean,
        ForeignKey = sqla.ForeignKey,
        relationship = orm.relationship,
        backref = orm.backref,
        ):
    """ creates base classes (BaseEdge and BaseNode) for use as mixins for
    graph nodes and edges. ALL parameters must be strings convertible to
    unicode!! Classes need to be subclassed/composited with a declarative_base
    class

        Parameters:
            :param NodeTable: the table for node (unicode)
            :param NodeClass: the class for node (unicode)
            :param EdgeTable: the table for edge (unicode)
            :param EdgeClass: the class for edge (unicode)

        you can see the docs on the module for more.
    returns (BaseNode, BaseEdge)
    to overwrite the default inheritance, you can pass in any SQLAlchemy
    classes used in creating the functions:
        declared_attr, Column, Unicode, Integer, Float, Boolean,
        relationship, backref, ForeignKey
            """
    # store inputted locals if provided
    NodeTable = NodeTable or class_to_tablename(NodeClass)
    EdgeTable = EdgeTable or class_to_tablename(EdgeClass)
    fdict = dict(NodeClass=NodeClass, EdgeClass=EdgeClass)
    class BaseNode(object):
        """ABC Node representation for SQLAlchemy nodes.
        Provides the following parameters:
            id - integer - primary key
            size - integer
            label - unicode
            color - unicode (10)
        Also has relationship to BaseEdge via:
            in_edges - edges where BaseNode is target
            out_edges - edges where BaseNode is source
        Does NOT define __init__"""
        @declared_attr
        def __tablename__(cls):
            return NodeTable
        id = Column(Integer, primary_key=True) # gephi (req)
        size = Column(Integer) # gephi (optional)
        label = Column(Unicode) # gephi (optional)
        color = Column(Unicode(10))

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
        def __repr__(self):
            return "<{cls}({vals})>".format(cls=self.__class__.__name__,
                    vals=repr([(k,getattr(self,k,None)) for k in self.attrs]))


    class BaseEdge(object):
        """ABC edge representation for declarative SQLAlchemy edges.
        Only source, target are required.
        Has the following parameters:
            id - integer, primary key
            size - integer
            label - unicode
            weight - float
            color - unicode(10)
        Connections:
            source_id - foreignkey to BaseNode - REQUIRED!
            target_id - foreignkey to TargetNode - REQUIRED!
            source - relationship/actual node that is the source of edge
            target - relationship/actual node that is target of edge
        __getitem__, __setitem__:
            __getitem__ --> returns id of source/target
                (so can use *edge operator with networkx, w/o maintaining refs)
            __setitem__ --> must set with BaseNode instance (otherwise
                ForeignKey could get *real messed up*)
        Does NOT define __init__
        """
        @declared_attr
        def __tablename__(self):
            return EdgeTable
        id = Column(Integer, primary_key=True)

        size = Column(Integer) # gephi (optional)
        label = Column(Unicode) # gephi (optional)
        weight = Column(Float) # gephi (optional)
        color = Column(Unicode(10))
        directed = Column(Boolean) # choices are 0, 1

        @declared_attr
        def source_id(self):
            return Column(Integer, ForeignKey(NodeTable + ".id"), nullable=False)

        @declared_attr
        def target_id(self):
            return Column(Integer, ForeignKey(NodeTable + ".id"), nullable=False)

        @declared_attr
        def source(self):
            return relationship(NodeClass,
                    primaryjoin="{NodeClass}.id == {EdgeClass}.source_id".format(**fdict), uselist=False,
                    backref=backref("out_edges"))

        @declared_attr
        def target(self):
            return relationship(NodeClass,
                primaryjoin="{NodeClass}.id == {EdgeClass}.target_id".format(**fdict), uselist=False,
                backref=backref("in_edges"))

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
            """ Note, only need to pass source, target or source_id, target_id """
            edge = cls.create(**kwargs)
            if source:
                edge.source = source
            if target:
                edge.target = target
            return edge
        def __repr__(self):
            return "<{cls}({vals})>".format(cls=self.__class__.__name__,
                    vals=repr([(k,getattr(self,k,None)) for k in self.attrs]))

    return BaseNode, BaseEdge
