"""
============
GraphAlchemy
============

Graph node-edge relationships in SQLAlchemy_ (and soon more orms) + networkx_
integration.

Documentation_ is available at http://graphalchemy.readthedocs.org

It's very simple to use (and examples are to come). But for now the best thing to do is
to go read the docs on SQLAlchemy_

A very minimal example (using an SQLite database)::

    >>> from graphalchemy.sqlmodels import create_base_classes, sqlite_connect
    >>> from sqlalchemy.ext.declarative import declarative_base
    >>>
    >>> Base = declarative_base()
    >>> Node, Edge = create_base_classes(NodeClass="Node", EdgeClass="Edge", Base=Base)
    >>> engine, session = sqlite_connect("database.db", metadata=Base.metadata)
    >>>
    >>> # be sure to use unicode!!
    >>> node1 = Node(label=u"First node!")
    >>> node2 = Node(label=u"Second node!")
    >>> node3 = Node(label=u"Third node!")
    >>> edge1 = Edge.connect_nodes(node1, node2)
    >>> edge2 = Edge.connect_nodes(node1, node3)
    >>>
    >>> session.add_all([node1, node2, node3, edge1, edge2])
    >>> session.commit()


.. _documentation : http://graphalchemy.readthedocs.org
.. _sqlalchemy : http://www.sqlalchemy.org/
.. _networkx : http://networkx.lanl.gov/
"""
