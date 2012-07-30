from graphalchemy import sqlmodels
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
Base = declarative_base()
Node, Edge = sqlmodels.create_base_classes("Node", "Edge", Base=Base)


DBPATH = os.path.abspath("quick_testdatabase.db")
SQLITEPATH = "sqlite:///" + DBPATH
def main(delete_db=False):
    # add these as globals so can use 'em quick
    global node1, node2, node3, edge, edge2, Base, engine, session
    if os.path.exists(DBPATH) and delete_db:
        os.remove(DBPATH)
    if not os.path.exists(DBPATH):
        # create the file with f.write
        with open(DBPATH, "wb") as f:
            f.write("")
    engine, session = sqlmodels.sqlite_connect(DBPATH, echo=True, metadata=Base.metadata)

    node1 = Node()
    node2 = Node()
    node3 = Node(label = u"NODE3!", size=4)
    edge = Edge.connect_nodes(source=node1, target=node2)
    edge2 = Edge.connect_nodes(source=node1, target=node3, label=u"ANOTHEREDGE!", weight=3.0)
    session.add_all([node1, node2, edge, node3, edge2])
    session.commit()
    print node1, node2, node3, edge, edge2

if __name__ == '__main__':
    main()
