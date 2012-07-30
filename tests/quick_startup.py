from graphalchemy import models
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
BaseNode, BaseEdge = models.create_base_classes("Node", "Edge")

Base = declarative_base()

DBPATH = os.path.abspath("quick_testdatabase.db")
SQLITEPATH = "sqlite:///" + DBPATH
class Node(Base, BaseNode): pass
class Edge(Base, BaseEdge): pass
def main(delete_db=False):
    # add these as globals so can use 'em quick
    global node1, node2, node3, edge, edge2, Base, Session, engine, session
    if os.path.exists(DBPATH) and delete_db:
        os.remove(DBPATH)
    if not os.path.exists(DBPATH):
        # create the file with f.write
        with open(DBPATH, "wb") as f:
            f.write("")
    engine = create_engine(SQLITEPATH, echo=True)
    Base.metadata.bind = engine
    Base.metadata.create_all()
    Session = sessionmaker(bind=engine)
    session = Session()

    node1 = Node()
    node2 = Node()
    node3 = Node(label = u"NODE3!", size=4)
    edge = Edge.connect_nodes(source=node1, target=node2)
    edge2 = Edge.connect_nodes(source=node1, target=node3, label=u"ANOTHEREDGE!", weight=3.0)
    session.add_all([node1, node2, edge, node3, edge2])
    session.commit()
if __name__ == '__main__':
    main(delete_db=True)
