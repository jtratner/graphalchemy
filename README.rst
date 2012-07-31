============
GraphAlchemy
============

.. contents::
    :depth: 2

Graph node-edge relationships in SQLAlchemy_ (and soon more orms) + networkx_
integration.

The Goal
========

Set up a generalized abstraction/interface for a graph that can be used across
various platforms and within various frameworks that is easy and simple to use,
extensible, and that easily hooks into other graphing tools (like gephi_
networkx_, etc.)

What's here
===========

A basic set of node/edge abstractions + many-to-one relationships for a graph
represented in SQL with SQLAlchemy_

Using this package
==================

Documentation_ is available at http://graphalchemy.readthedocs.org

It's very simple to use (and examples are to come). But for now the best thing to do is
to go read the docs on SQLAlchemy_

A very minimal example (using an SQLite database)::

    from graphalchemy.sqlmodels import create_base_classes, sqlite_connect
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()
    Node, Edge = create_base_classes(NodeClass="Node", EdgeClass="Edge", Base=Base)
    engine, session = sqlite_connect("database.db", metadata=Base.metadata)

    # be sure to use unicode!!
    node1 = Node(label=u"First node!")
    node2 = Node(label=u"Second node!")
    node3 = Node(label=u"Third node!")
    edge1 = Edge.connect_nodes(node1, node2)
    edge2 = Edge.connect_nodes(node1, node3)

    session.add_all([node1, node2, node3, edge1, edge2])
    session.commit()


    # now we can graph it

    import networkx as nx
    G = nx.Graph()
    G.add_edges_from([edge1, edge2])

    # now we can draw this! (if you had pylab, matplotlib, etc)

And you'd get a picture that looked something like this (clearly, we haven't added all the traits
and such in, but you get the idea):

.. image:: https://github.com/jtratner/graphalchemy/raw/master/docs/images/readme-example.png

Now, obviously this is a pretty minimal example, but it shows how you can take advantage
of the power of SQL joins, queries, etc, but also very easily 

What's going to be here
=======================

1. networkx_ integration
2. testing for multiple sql databases and adapters
3. abstractions for Google App Engine, mongoalchemy_, and possibly Django ORM
4. adapter between networkx_ and web service requests (maybe?)

Testing coverage
================

Basic test suite that gets 100% line coverage for SQLAlchemy models and base
models (still missing a test for Flask-SQLAlchemy). I've only run it on SQLite
so far, but presumably it should work with other SQL databases just fine (since
it uses SQLAlchemy's `declarative base`_)

.. _sqlalchemy : http://www.sqlalchemy.org/
.. _networkx : http://networkx.lanl.gov/
.. _mongoalchemy : http://www.mongoalchemy.org/
.. _gephi : http://gephi.org/
.. _declarative base : http://docs.sqlalchemy.org/en/rel_0_7/orm/extensions/declarative.html
.. _documentation : http://graphalchemy.readthedocs.org
