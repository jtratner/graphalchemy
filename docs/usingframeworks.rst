=====================================================
Notes on integrating GraphAlchemy with web frameworks
=====================================================

Flask
=====

There are a few different options for :ref:`using Flask with SQLAlchemy
<flask:patterns:sqlalchemy>`, which you can read about on `Flask's
docs`_.

Using Flask-SQLAlchemy plugin
-----------------------------

The only real caveat is that if you want to use :mod:`Flask-SQLAlchemy`, you
should use the :func`~graphalchemy.sqlmodels.create_flask_classes`
function, and pass it an :class:`SQLAlchemy` instance (usually called
db).

Pyramid (prev Pylons)
=====================

Pyramid has a cookbook entry on :ref:`using SQLAlchemy with Pyramid
<pyramidcookbook:SQLAlchemy>`. But it's basically just normal use of
SQLAlchemy, with a few specific notes on using Pyramid's :class:`DBSession`
for sessions and some advanced topics that aren't really relevant here.


webapp2
=======

webapp2_ should work without a problem, just import it and use it like
you would with SQLAlchemy (probably just use it straight up?)

Incompatible frameworks (for now)
=================================

Google App Engine
-----------------

`Google App Engine`_ doesn't have a (standard) relational database,
but a future version of :mod:`graphalchemy` will have a version that
works with App Engine (though it may or may not be a really efficient
solution).

Django
------

Django uses its own ORM (which you can replace with SQLAlchemy, but it means
you lose much of Django's functionality). There may be a future version of
:mod:`graphalchemy` that will support Django, but for the moment, you'd
have to choose to use SQLAlchemy.


.. _webapp2 : http://webapp-improved.appspot.com/
.. _Google App Engine : https://developers.google.com/appengine/
.. _Flask's docs: http://flask.pocoo.org/docs/patterns/sqlalchemy
