from graphalchemy.sqlmodels import (
        create_base_classes,
        sqlite_connect,
        class_to_tablename,
        )
# TODO: add flask-sqlalchemy tests
from nose.tools import assert_equal, raises
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import (
        IntegrityError)
import unittest
import os

from collections import namedtuple
DBObject = namedtuple("DBObject", ["Node", "Edge", "Base", "engine", "Session", "session"])
def make_DBObject(Node=None, Edge=None, Base=None, engine=None, Session=None, session=None):
    """ convenience method for object creation """
    return DBObject(Node, Edge, Base, engine, Session, session)

def test_class_to_tablename1():
    """ class_to_tablename: lowercase remains lowercase"""
    for klass in ("apples", "bananas", "carrots", "yeah_man", "course_nodes", "course_edges"):
        assert_equal(class_to_tablename(klass), klass)

def test_class_to_tablename2():
    """ class_to_tablename: (CamelCase --> camel_case) CamelCase should always get underscores """
    for klass, output in [("CamelCase", "camel_case"), ("CourseNode", "course_node"), ("CourseEdge", "course_edge")]:
        assert_equal(class_to_tablename(klass), output)
def test_class_to_tablename3():
    """ class_to_tablename: sequential uppercase get multiple underscores (someDB --> some_d_b)"""
    for klass, output in [("someDB", "some_d_b"), ("CCamelCCase", "c_camel_c_case"), ("ABCDEFG", "a_b_c_d_e_f_g")]:
        assert_equal(class_to_tablename(klass), output)

BLANKDATABASE = "tests/testdatabase.db"
PRESETDATABASE = "tests/testcompatibledb.db"
class DBSetup(object):
    @classmethod
    def create_database(cls, dbpath,
            baseclass=None,
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
                EdgeTable=EdgeTable)

        cls.Base = Base = baseclass or declarative_base()
        node_bases = [Base, BaseNode]
        edge_bases = [Base, BaseEdge]

        if NodeMixin:
            node_bases.append(NodeMixin)
        if EdgeMixin:
            edge_bases.append(EdgeMixin)

        # dynamically create classes
        cls.Node = Node = type("Node", tuple(node_bases), {})
        cls.Edge = Edge = type("Edge", tuple(edge_bases), {})

        cls.engine = engine = create_engine(dbpath)
        # load tables
        Base.metadata.bind = engine
        Base.metadata.create_all()

        cls.Session = Session = sessionmaker(bind=engine)
        cls.session = session = Session()
        return make_DBObject(Node=Node, Edge=Edge, engine=engine, Base=Base,
                session=session, Session=Session)

def check_object_characteristics(object, attributes):
    assert object
    for k,v in attributes.items():
        assert_equal((k, getattr(object, k, None)), (k , v))

class TestBasicTables(unittest.TestSuite, DBSetup):
    dbpath = os.path.abspath(BLANKDATABASE)
    sqlitedbpath = "sqlite:///" + dbpath
    @classmethod
    def setUpClass(cls):
        if os.path.exists(cls.dbpath):
            os.path.remove(cls.dbpath)
        if not os.path.exists(cls.dbpath):
            # create the file
            with open(cls.dbpath, "wb") as f:
                f.write("")
        cls.node1_attrs = {}
        cls.node2_attrs = {}
        cls.edge12_attrs = {}
        cls.edge21_attrs = {}
        cls.create_database(cls.sqlitedbpath)

    def create_nodes(self, nodes):
        return [self.Node(**kwargs) for kwargs in nodes]

    def create_edges(self, edges):
        return [self.Edge(**kwargs) for kwargs in edges]

    def get_edge(self, id):
        edge = self.session.query(self.Edge).get(id)
        assert isinstance(edge, self.Edge), "query didn't create an instance of Edge class"
        return edge

    def get_node(self, id):
        node = self.session.query(self.Node).get(id)
        assert isinstance(node, self.Node), "query didn't create an instance of Node class"
        return node

    def test1_create_nodes(self):
        """test creating and committing nodes """
        node1, node2 = self.create_nodes([dict(label=u"Node1", size=15,
            color=u"blue"), dict(label=u"Node2", size=1, color=u"orange")])
        self.session.add_all([node1, node2])
        self.session.commit()
        self.node1_attrs.update(dict(
                id = node1.id,
                label = u"Node1",
                size = 15,
                color = u"blue",))
        self.node2_attrs.update(dict(
                id = node2.id,
                label = u"Node2",
                size = 1,
                color = u"orange",))

    def expire_and_create_session(self):
        self.session.expire_all()
        self.session.close()
        self.session = self.Session()

    def test2_connect_nodes(self):
        """test creating a forward and reverse connection between nodes"""
        node1 = self.get_node(self.node1_attrs["id"])
        node2 = self.get_node(self.node2_attrs["id"])
        edge12 = self.Edge.connect_nodes(source=node1,
                target=node2, label=u"Edge12", size=5, weight=3)
        edge21 = self.Edge.connect_nodes(source=node2,
                target=node1, label=u"Edge21", size=10, weight=3)
        self.session.add_all([edge12, edge21])
        self.session.commit()
        self.edge12_attrs.update(dict(
                id = edge12.id,
                source_id = node1.id,
                target_id = node2.id,
                label = u"Edge12",
                size=5,
                weight=3))
        self.edge21_attrs.update(dict(
                id = edge21.id,
                source_id = node2.id,
                target_id = node1.id,
                label = u"Edge21",
                size=10,
                weight=3))
        # check that source and target were correct
        check_object_characteristics(edge12, self.edge12_attrs)
        check_object_characteristics(edge21, self.edge21_attrs)
        # get rid of all nodes and edges from reference in object
        del node1
        del node2
        del edge12
        del edge21


    def test3_can_query_edges_via_id(self):
        """ after querying edges, they still have correct id"""
        self.expire_and_create_session()
        edge12 = self.get_edge(self.edge12_attrs["id"])
        edge21 = self.get_edge(self.edge21_attrs["id"])
        check_object_characteristics(edge12, self.edge12_attrs)
        check_object_characteristics(edge21, self.edge21_attrs)

    def test4_can_query_nodes_via_id(self):
        """ after querying nodes, they should have the correct ids and labels"""
        self.expire_and_create_session()
        node1 = self.get_node(self.node1_attrs["id"])
        node2 = self.get_node(self.node2_attrs["id"])
        check_object_characteristics(node1, self.node1_attrs)
        check_object_characteristics(node2, self.node2_attrs)

    def test3_getting_nodes_via_edges(self):
        """ test calling nodes via edges"""
        self.expire_and_create_session()
        edge12 = self.get_edge(self.edge12_attrs["id"])
        check_object_characteristics(edge12.source, self.node1_attrs)
        check_object_characteristics(edge12.target, self.node2_attrs)

    def test31_getting_nodes_via_edges(self):
        """ test calling nodes via edges"""
        edge21 = self.get_edge(self.edge21_attrs["id"])
        check_object_characteristics(edge21.source, self.node2_attrs)
        check_object_characteristics(edge21.target, self.node1_attrs)


    def test4_getting_edges_via_nodes(self):
        """ test getting edges via nodes (and that ordering is correct) """
        self.expire_and_create_session()
        node1 = self.get_node(self.node1_attrs["id"])
        edge12 = node1.out_edges[0]
        check_object_characteristics(edge12, self.edge12_attrs)
        edge21 = node1.in_edges[0]
        check_object_characteristics(edge21, self.edge21_attrs)

    def test41_getting_edges_via_nodes(self):
        """ test getting edges via nodes (and that ordering is correct) """
        self.expire_and_create_session()
        node2 = self.get_node(self.node1_attrs["id"])
        edge12 = node2.out_edges[0]
        check_object_characteristics(edge12, self.edge12_attrs)
        edge21 = node2.in_edges[0]
        check_object_characteristics(edge21, self.edge21_attrs)
    @classmethod
    def tearDownClass(cls):
        # this should delete the database
        cls.Base.metadata.drop_all()
        os.remove(cls.dbpath)

class DummyClass(object):
    """ test class for creating objects with attributes """
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class TestSpecialMethods(TestBasicTables):
    @classmethod
    def setUpClass(cls):
        if os.path.exists(cls.dbpath):
            os.path.remove(cls.dbpath)
        if not os.path.exists(cls.dbpath):
            # create the file
            with open(cls.dbpath, "wb") as f:
                f.write("")
        cls.create_database(cls.sqlitedbpath)

    @raises(IntegrityError)
    def test_empty_edge_create_raises_error(self):
        """check that Edge.create fails without source/target"""
        try:
            self.session.add(self.Edge.create(DummyClass()))
            self.session.commit()
        finally:
            self.session.rollback()

    @raises(IntegrityError)
    def test_empty_edge_raises_error(self):
        """check that Edge fails without source/target"""
        try:
            self.session.add(self.Edge())
            self.session.commit()
        finally:
            self.session.rollback()

    def test_edge_can_take_id(self):
        """ If edge gets target_id and source_id, it should work fine """
        node1 = self.Node()
        node2 = self.Node()
        self.session.add_all([node1, node2])
        self.session.commit()
        assert node1
        assert node2
        edge = self.Edge(target_id = node1.id, source_id = node2.id)
        self.session.add(edge)
        self.session.commit()
        assert edge
        assert node1 is edge.target
        assert node2 is edge.source

    def test_edge_create_takes_id(self):
        self.expire_and_create_session()
        node1, node2 = list(self.session.query(self.Node).all())[0:2]
        node1_id, node2_id = node1.id, node2.id
        node3 = self.Node()
        self.session.add(node3)
        self.session.commit()
        edge = self.Edge.create(source_id = node1.id, target_id = node3.id)
        node3_id = node3.id
        self.session.add(edge)
        self.session.commit()
        edge_id = edge.id
        assert edge
        self.expire_and_create_session()
        edge = self.get_edge(edge_id)
        node1 = self.get_node(node1_id)
        node3 = self.get_node(node3_id)
        assert_equal(edge.source, node1)
        assert_equal(edge.target, node3)

    def __iter__(self):
        # use iter to only run specific tests
        tests = [self.test_empty_edge_create_raises_error,
                self.test_empty_edge_raises_error,
                self.test_edge_can_take_id,
                self.test_edge_create_takes_id,
                ]
        for test in tests:
            yield test
