.. py:currentmodule:: graphalchemy.sqlmodels

Creating Declarative Base Classes for SQLAlchemy
================================================

.. autofunction:: graphalchemy.sqlmodels.create_base_classes (NodeClass, EdgeClass, [NodeTable = None, [EdgeTable = None, [declared_attr, [Column, [Integer, [Unicode, [Float, [Boolean, [ForeignKey, [relationship, [backref, [Base = None,)


Creating Base Classes for Flask-SQLAlchemy
==========================================

.. autofunction:: graphalchemy.sqlmodels.create_flask_classes

Other Methods
=============

.. autofunction:: graphalchemy.sqlmodels.sqlite_connect (dbpath, metadata, [create_engine, [sessionmaker, [echo=True]]])

