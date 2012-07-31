"""
Models:

    this module allows the creation of a few base classes to make it easier
    to work with SQLAlchemy in creating (directed/undirected) graphs and edges.

NOTE: If you feel the need to typecheck, it may be better to use basemodels.BaseEdge and
basemodels.BaseNode as types, since those will *always* be True for any
class created here.
"""
try:
    import sqlalchemy as sqla # Column, Integer, Unicode, Float, Boolean, ForeignKey
except ImportError:
    raise ImportError("Must have SQLAlchemy installed to use sqlmodelss")
from basemodels import BaseEdge, BaseNode
import sqlalchemy.ext.declarative as decl # declared_attr
import sqlalchemy.orm as orm # relationship, backref
# overwrite a few extensions to use flask-sqlalchemy's model
import os

def sqlite_connect(dbpath, metadata, echo=True, enforce_fk=True, **kwargs):
    """ return an sqllite connection to the given dbpath.
    Optional arguments default to sqlalchemy functions.

    Parameter:

        :param dbpath: path (relative or absolute) to database (unicode/string) NOT "sqlite://"
        :param metadata: something that supports create_all() to create/load tables and has a bind attribute
        :type metadata: should create tables with `create_all()`
        :type create_engine: function (dbpath) -> engine
        :param sessionmaker: (optional) must take `bind=engine`, return a class that can be called
                            to create a session
        :type sessionamker: function (bind=engine) --> Session
        :param event: event creator for engine (from SQLAlchemy)
        :param bool enforce_fk: set database to enforce foreign key relationships
        :default enforce_fk: True

    Returns:

       :returns: (engine, session)

       :raises: ValueError if passed a path that does not exist or a non-valid path.

    """

    create_engine = kwargs.get("create_engine") or sqla.create_engine
    sessionmaker = kwargs.get("sessionmaker") or orm.sessionmaker
    event = kwargs.get("event") or sqla.event

    if dbpath.startswith("sqlite://"):
        raise ValueError("Must give path, not sqlite connection string")
    if (not os.path.exists(dbpath)) or os.path.isdir(dbpath):
        raise ValueError("Path does not exist or is directory: %s." % dbpath)
    dbpath = os.path.abspath(dbpath)
    engine = create_engine("sqlite:///" + dbpath, echo=echo)
    if enforce_fk:
        def _fk_pragma_on_connect(dbapi_con, con_record):
            """ set enforced foreignkey for sqlite """
            dbapi_con.execute('pragma foreign_keys=on')
        event.listen(engine, 'connect', _fk_pragma_on_connect)
    metadata.bind = engine
    metadata.create_all()
    Session = sessionmaker(bind=engine)
    session = Session()
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


def create_base_classes( NodeClass, EdgeClass, NodeTable = None, EdgeTable =
        None, Base = None, **kwargs):
    """ creates base classes (BaseEdge and BaseNode) for use as mixins for
    graph nodes and edges. ALL parameters must be strings convertible to
    unicode! Classes need to be subclassed/composited with a declarative_base
    class

    Parameters:
        :param NodeTable: the table for node (unicode)
        :param NodeClass: the class for node (unicode)
        :param EdgeTable: the table for edge (unicode)
        :param EdgeClass: the class for edge (unicode)
        :param Base: (optional) if a Base is passed, it will be
                    added to the class type for you, thereby requiring
                    no subclassing on your part.
        :type Base: SQLAlchemy declarative base

    :returns: tuple of Node, Edge classes
    :rtype: (:class:`Node`, :class:`Edge`)

    NOTE: To overwrite the default inheritance, you can pass in any SQLAlchemy
    classes used in creating the functions as a keyword argument::

        declared_attr, Column, Unicode, Integer, Float, Boolean,
        relationship, backref, ForeignKey

            """
    declared_attr = kwargs.get("declared_attr") or decl.declared_attr
    Column = kwargs.get("Column") or sqla.Column
    Integer = kwargs.get("Integer") or sqla.Integer
    Unicode = kwargs.get("Unicode") or sqla.Unicode
    Float = kwargs.get("Float") or sqla.Float
    Boolean = kwargs.get("Boolean") or sqla.Boolean
    ForeignKey = kwargs.get("ForeignKey") or sqla.ForeignKey
    relationship = kwargs.get("relationship") or orm.relationship
    backref = kwargs.get("backref") or orm.backref
    # store inputted locals if provided
    NodeTable = NodeTable or class_to_tablename(NodeClass)
    EdgeTable = EdgeTable or class_to_tablename(EdgeClass)
    fdict = dict(NodeClass=NodeClass, EdgeClass=EdgeClass)

    class Node(BaseNode):
        """ SQLAlchemy declarative base for a Node representation

        Implements the BaseNode ABC:

        {BaseNode}""".format(BaseNode=BaseNode.__doc__)
        @declared_attr
        def __tablename__(cls):
            return NodeTable
        id = Column(Integer, primary_key=True) # gephi (req)
        size = Column(Integer) # gephi (optional)
        label = Column(Unicode) # gephi (optional)
        color = Column(Unicode(10))



    class Edge(BaseEdge):
        """ SQLAlchemy declarative base for edge representation.

        Implements the BaseEdgeABC:

        {BaseEdge}""".format(BaseEdge=BaseEdge.__doc__)
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

    # if given a base class then return a fully functional class
    if Base:
        Node = type(NodeClass, (Node, Base), {})
        Edge = type(EdgeClass, (Edge, Base), {})
    return Node, Edge

def create_flask_classes(
        db,
        NodeClass,
        EdgeClass,
        NodeTable = None,
        EdgeTable = None,
        ):
    """ Convenience method for creating Node and Edge base classes for use with
    :mod:`Flask-SQLAlchemy`. Has nearly the same signature as :meth:`create_base_classes`
    But does not take in any overriding methods. Only NodeClass and EdgeClass
    are required.

    The one required parameter is `db`, which you must create first from the
    sqlalchemy directions.  Example usage:

    >>> from flask import Flask
    >>> from flask.ext.sqlalchemy import SQLAlchemy
    >>> from graphalchemy.sqlmodelss import create_flask_classes
    >>>
    >>> app = Flask(__name__)
    >>> app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    >>> db = SQLAlchemy(app)
    >>>
    >>> Node, Edge = create_flask_classes(db, "Node", "Edge")

    At this point, you can subclass `Node` and `Edge` to add additional
    traits; however, both `Node` and `Edge` will *already* be subclasses of
    db.Model, so you don't need to mix that in.

    Or you can just start up your database with:

    >>> db.create_all()

    Otherwise, the classes created by :meth:`create_flask_classes` and
    :meth:`create_base_classes` are pretty much the same, except that
    :mod:`Flask-SQLAlchemy` provides some additional features that can be accessed
    on the Models.
    """

    return create_base_classes(
        NodeClass = NodeClass,
        EdgeClass = EdgeClass,
        NodeTable = NodeTable,
        EdgeTable = EdgeTable,
        declared_attr = db.declared_attr,
        Column = db.Column,
        Integer = db.Integer,
        Unicode = db.Unicode,
        Float = db.Float,
        Boolean = db.Boolean,
        ForeignKey = db.ForeignKey,
        relationship = db.relationship,
        backref = db.backref,
        Base = db.Model)
