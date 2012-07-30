"""
utilities for testing sqlmodels
"""
from graphalchemy.sqlmodels import (
        create_base_classes,
        sqlite_connect,
        )
from general_utils import simple_decorator
from nose.tools import assert_equal, nottest
# TODO: add flask-sqlalchemy tests
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os


from collections import namedtuple
DBObject = namedtuple("DBObject", ["Node", "Edge", "Base", "engine", "Session", "session"])
def make_DBObject(Node=None, Edge=None, Base=None, engine=None, Session=None, session=None):
    """ convenience method for object creation """
    return DBObject(Node, Edge, Base, engine, Session, session)

def show_table_decorator(table_attrs=None, other_attrs=None):
    """ decorator to show tables on error, so they appear in std out """
    @simple_decorator
    def decorator(f):
        def _f(self, *args, **kwargs):
            try:
                return f(self, *args, **kwargs)
            except:
                if table_attrs:
                    print "\n----------\nTables:"
                    for attr in table_attrs:
                        if getattr(self, attr, None):
                            print getattr(self, attr).__table__
                    print "\n----------"
                if other_attrs:
                    print "\n----------\nOther attributes:"
                    for attr in other_attrs:
                        if getattr(self, attr, None):
                            print getattr(self, attr)
                    print "\n----------"
                if getattr(self, "session", None):
                    self.session.rollback()
                raise

        return _f
    return decorator

show_tables = show_table_decorator(table_attrs = ["Node", "Edge"])

class DBSetup(object):
    """ base class for testing database setups,
    all you need to have is a dbpath defined in the class"""
    @classmethod
    def setUpClass(cls):
        cls.create_database("sqlite:///" + cls.dbath)
    @classmethod
    def create_database(cls, dbpath,
            Base=None,
            NodeClass=None,
            EdgeClass=None,
            NodeTable=None,
            EdgeTable=None,
            NodeMixin=None,
            EdgeMixin=None,
            connect=sqlite_connect,
            echo=True,
            declarative_base=declarative_base,
            sessionmaker=sessionmaker,
            create_engine=create_engine):
        """ sets up database, engine, connection.
        and initializes database.
        sets all items as attributes on class, but can also access dbobject
        Returns DBObject (nodeclass, edgeclass, Base, engine, Session, session)
        """
        NodeClass = NodeClass or "Node"
        EdgeClass = EdgeClass or "Edge"

        BaseNode, BaseEdge = create_base_classes(
                NodeClass=NodeClass,
                EdgeClass=EdgeClass,
                NodeTable=NodeTable,
                EdgeTable=EdgeTable,
                Base=Base)
        if Base is None:
            cls.Base = Base = declarative_base()
            node_bases = [Base, BaseNode]
            edge_bases = [Base, BaseEdge]
        else:
            cls.Base = Base
            node_bases = [BaseNode]
            edge_bases = [BaseEdge]

        if NodeMixin:
            node_bases.append(NodeMixin)
        if EdgeMixin:
            edge_bases.append(EdgeMixin)

        # dynamically create classes
        extend_existing_opt = {"__table_args__":{"extend_existing":True}}
        cls.Node = Node = type("Node", tuple(node_bases), dict(extend_existing_opt))
        cls.Edge = Edge = type("Edge", tuple(edge_bases), dict(extend_existing_opt))
        if not dbpath.startswith("sqlite://"):
            dbpath = "sqlite:///" + os.path.abspath(dbpath)
        cls.engine = engine = create_engine(dbpath)
        # load tables
        Base.metadata.bind = engine
        Base.metadata.create_all()

        cls.Session = Session = sessionmaker(bind=engine)
        cls.session = session = Session()
        return make_DBObject(Node=Node, Edge=Edge, engine=engine, Base=Base,
                session=session, Session=Session)
    @show_tables
    def create_nodes(self, nodes):
        return [self.Node(**kwargs) for kwargs in nodes]

    @show_tables
    def create_edges(self, edges):
        return [self.Edge(**kwargs) for kwargs in edges]

    @show_tables
    def get_edge(self, id):
        edge = self.session.query(self.Edge).get(id)
        assert isinstance(edge, self.Edge), "query didn't create an instance of Edge class"
        return edge

    @show_tables
    def get_node(self, id):
        node = self.session.query(self.Node).get(id)
        assert isinstance(node, self.Node), "query didn't create an instance of Node class"
        return node

    @show_tables
    def expire_and_create_session(self):
        self.session.expire_all()
        self.session.close()
        self.session = self.Session()
    @classmethod
    def tearDownClass(cls):
        # this should delete the database
        cls.Base.metadata.drop_all()
        cls.delete_items()
        os.remove(cls.dbpath)
    @classmethod
    def delete_items(cls, itemlist=None):
        """ remove leftovers so class can be reused"""
        if itemlist:
            for item in itemlist:
                delattr(cls, item)
        for item in ("Session", "session", "engine", "Node", "Edge"):
            try:
                delattr(cls, item)
            except:
                pass

def check_object_characteristics(object, attributes):
    assert object
    for k,v in attributes.items():
        assert_equal((k, getattr(object, k, None)), (k , v))

@nottest
def limit_tests_to(testlist):
    """ creates an __iter__ method that only tests the tests in testlist 
    (testlist should be a list of strings/getattr-able items)"""
    def __iter__(self):
        # use iter to only run specific tests
        for test in testlist:
            yield getattr(self, test)
    return __iter__
