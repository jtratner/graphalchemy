from sqlmodelutils import (
        # DBObject, make_DBObject,
        DBSetup, check_object_characteristics,
        limit_tests_to, show_tables)
from graphalchemy.sqlmodels import (
        sqlite_connect,
        class_to_tablename,
        create_base_classes
        )
from graphalchemy.basemodels import BaseNode, BaseEdge
from sqlalchemy.ext.declarative import declarative_base
# TODO: add flask-sqlalchemy tests
from nose.tools import assert_equal, raises
from sqlalchemy.exc import (
        IntegrityError)
import unittest
import os

@raises(ValueError)
def test_sqlite_connect_error():
    """ sqlite connect should raise a ValueError if the path doesn't exist """
    path = "Iamreallyhappy.db"
    while os.path.exists(path):
        path = "a" + path
    return sqlite_connect(path, None)

@raises(ValueError)
def test_sqlite_path_error():
    """ sqlite connect should raise a ValueError if you pass it  "sqlite:///"-starting path """
    path = "sqlite:////Iamreallyhappy.db"
    return sqlite_connect(path, None)

@raises(ValueError)
def test_sqlite_path_exists_error():
    """ sqlite_connect should raise a ValueError if passed a "sqlite:///"-starting path that exists """
    path = "asdfasfasdf.db"
    while os.path.exists(path):
        path = "z" + path
    with open(path, "wb") as f:
        f.write("")
    newpath = "sqlite:///" + path
    try:
        return sqlite_connect(newpath, None)
    except:
        raise
    finally:
        os.remove(path)

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

BLANKDATABASE = "testdatabase.db"
PRESETDATABASE = "testcompatibledb.db"


class DummyClass(object):
    """ test class for creating objects with attributes """
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class TestBasicTables(unittest.TestSuite, DBSetup):
    dbpath = os.path.abspath(BLANKDATABASE)
    sqlitedbpath = "sqlite:///" + dbpath
    @classmethod
    def setUpClass(cls):
        if os.path.exists(cls.dbpath):
            os.remove(cls.dbpath)
        if not os.path.exists(cls.dbpath):
            # create the file
            with open(cls.dbpath, "wb") as f:
                f.write("")
        cls.node1_attrs = {}
        cls.node2_attrs = {}
        cls.edge12_attrs = {}
        cls.edge21_attrs = {}
        cls.create_database(cls.sqlitedbpath)
    @show_tables
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

    @raises(IndexError)
    def test14_set_index_error(self):
        """ edges can only hold two nodes"""
        anode = self.Node()
        bnode = self.Node()
        cnode = self.Node()
        edge = self.Edge()
        edge[0] = anode
        edge[1] = bnode
        edge[2] = cnode

    @raises(IndexError)
    def test15_get_index_error(self):
        """ edges can only be asked for two nodes"""
        anode = self.Node()
        bnode = self.Node()
        edge = self.Edge()
        edge[0] = anode
        edge[1] = bnode
        print edge[2]

    @raises(TypeError)
    def test16_set_only_nodes(self):
        """ only BaseNodes can be stored in edges """
        edge = self.Edge()
        edge[0] = 5
        edge[1] = None
    
    def test44_created_nodes_and_edges(self):
        """ nodes and edges can be created from objects with `create`"""
        myobj = DummyClass()
        myobj.label = u"Dummy Label"
        myobj.size = 15.0
        myobj.color = u"Green"
        other = DummyClass()
        other.label = u"YES!"
        other.size = 22.0
        other.color = u"Fuschia"
        newnode = self.Node.create(myobj)
        self.session.add(newnode)
        self.session.commit()
        assert all([myobj.label == u"Dummy Label",
        myobj.size == 15.0,
        myobj.color == u"Green"]), "object was mutated during `create`"
        othernode = self.Node.create(other)
        assert all([
        other.label == u"YES!",
        other.size == 22.0,
        other.color == u"Fuschia"]), "object was mutated during `create`"
        assert_equal((other.label, other.size, other.color), 
                (othernode.label, othernode.size, othernode.color))
        assert isinstance(othernode, BaseNode), "`create` didn't produce an instance of BaseNode (%r). Instead was: %r" % (BaseNode, othernode.__class__.mro())
        assert isinstance(othernode, self.Node), "`create` didn't produce an instance of *Node*"
        new_edge = self.Edge.create(other, source=newnode, target=othernode)
        self.session.add(new_edge)
        self.session.commit()
        assert isinstance(new_edge, BaseEdge), "`create` didn't produce an instance of %r. Instead was: %r" % (BaseEdge, new_edge.__class__.mro())
        assert isinstance(new_edge, self.Edge), "`create` didn't produce an instance of %r. Instead was %r" % (self.Node, new_edge.__class__.mro())
        assert_equal(str(new_edge),"({src}, {tgt})".format(src=newnode.id, tgt=othernode.id))
        assert str(othernode).startswith("<Node")



    @classmethod
    def tearDownClass(cls):
        # this should delete the database
        cls.delete_items()
        os.remove(cls.dbpath)



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

    @classmethod
    def tearDownClass(cls):
        # this should delete the database
        cls.Base.metadata.drop_all()
        cls.delete_items()
        os.remove(cls.dbpath)
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

    __iter__ = limit_tests_to(["test_empty_edge_create_raises_error",
                "test_empty_edge_raises_error",
                "test_edge_can_take_id",
                "test_edge_create_takes_id",
                ])

class TestPassingBaseClass(TestSpecialMethods):
    """ runs the same tests as BasicTables, but this time with a defined Base"""
    @classmethod
    def setUpClass(cls):
        cls.tearDownClass()
        Base = declarative_base()
        Node, Edge = create_base_classes("Node", "Edge", Base=Base)
        cls.Node = Node
        cls.Edge = Edge
        cls.Base = Base
        if not os.path.exists(cls.dbpath):
            with open(cls.dbpath, "wb") as f:
                f.write("")
        engine, session = sqlite_connect(cls.dbpath, cls.Base.metadata)
        cls.engine = engine
        cls.session = session
        cls.Session = cls.session.__class__
        cls.session = session
    def test000_sqlite_connect(self):
        node15 = self.Node()
        self.session.add(node15)
        self.session.commit()
        self.engine = self.engine
    def test11_get_and_set(self):
        """ edges should be able to be accessed with *edge and edge[0], edge[1] """
        self.expire_and_create_session()
        node1 = self.Node(label=u"I am node 1!")
        node2 = self.Node(label=u"I am node 2!")
        node3 = self.Node(label=u"I am node 3!")
        node4 = self.Node()
        node5 = self.Node()
        edge1 = self.Edge.connect_nodes(source=node1, target=node2)
        edge2 = self.Edge.connect_nodes(source=node3, target=node1)
        edge3 = self.Edge.connect_nodes(source=node5, target=node1)
        nodelist = [node1, node2, node3, node4, node5]
        edgelist = [edge1, edge2, edge3]
        self.session.add_all(nodelist)
        self.session.add_all(edgelist)
        self.session.commit()
        def equal_id(id1, id2):
            assert id1 == id2, "The ids weren't equal from __getitem__: %r != %r" % (id1, id2)
        equal_id(edge1[0], node1.id)
        equal_id(edge1[1], node2.id)
        # test that the splat operator works as expected
        assert_equal((lambda *args: args)(*edge2), (node3.id, node1.id))
        edge4 = self.Edge()
        edge4[0] = node4
        edge4[1] = node5
        self.session.add(edge4)
        self.session.commit()
        edgelist.append(edge4)
        self.__class__.edge_ids = map(lambda x: x.id, edgelist)
        self.__class__.node_ids = map(lambda x: x.id, nodelist)
        # edge5 = self.Edge()
        # # edge5[0:1] = (node4, node5)
        # self.session.add(edge5)
        # self.session.commit()
        # node_ids = map(lambda x: x.id, nodelist)
        # edge_ids = map(lambda x: x.id, edgelist)
        # self.expire_and_create_session()
        # node1 = self.session.query(self.Node).get(node_ids[0])
    def test12_iteration_methods(self):
        """ test that iter_edge_targets actually returns all connecting nodes and edges """
        self.expire_and_create_session()
        node1 = self.session.query(self.Node).get(self.node_ids[0])
        edges, nodes = zip(*node1.iter_edge_targets())
        edge_ids = self.edge_ids[0:3]
        node_ids = [self.node_ids[1], self.node_ids[2], self.node_ids[4]]
        assert_equal(set(x.id for x in edges), set(edge_ids))
        assert_equal(set(x.id for x in nodes), set(node_ids))
    def test13_node_neighbors(self):
        """ nodes should return their neighbors when asked """
        node1 = self.session.query(self.Node).get(self.node_ids[0])
        assert_equal(set(x.id for x in node1.edges), set(self.edge_ids[0:3]))
        assert_equal(set(node1.neighbors), set(map(lambda x: self.session.query(self.Node).get(x), 
                                        [self.node_ids[1], self.node_ids[2], self.node_ids[4]])))

    @classmethod
    def tearDownClass(cls):
        # this should delete the database
        cls.delete_items()
        if os.path.exists(cls.dbpath):
            os.remove(cls.dbpath)
