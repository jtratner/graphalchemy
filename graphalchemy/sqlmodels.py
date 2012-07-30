"""
Models:

    this module allows the creation of a few base classes to make it easier
    to work with SQLAlchemy in creating (directed/undirected) graphs and edges.

NOTE: If you feel the need to typecheck, it may be better to use basemodel.BaseEdge and
basemodel.BaseNode as types, since those will *always* be True for any
class created here.
"""
from base_model import BaseEdge, BaseNode
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
        Base = None
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
            :param Base: (optional) if a Base is passed, it will be
                        added to the class type for you, thereby requiring
                        no subclassing on your part.
            :type Base: SQLAlchemy declarative base

        you can see the docs on the module for more.
    returns (Node, Edge)
    to overwrite the default inheritance, you can pass in any SQLAlchemy
    classes used in creating the functions:
        declared_attr, Column, Unicode, Integer, Float, Boolean,
        relationship, backref, ForeignKey
            """
    # store inputted locals if provided
    NodeTable = NodeTable or class_to_tablename(NodeClass)
    EdgeTable = EdgeTable or class_to_tablename(EdgeClass)
    fdict = dict(NodeClass=NodeClass, EdgeClass=EdgeClass)

    class Node(BaseNode):
        @declared_attr
        def __tablename__(cls):
            return NodeTable
        id = Column(Integer, primary_key=True) # gephi (req)
        size = Column(Integer) # gephi (optional)
        label = Column(Unicode) # gephi (optional)
        color = Column(Unicode(10))



    class Edge(BaseEdge):
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
