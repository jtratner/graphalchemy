"""
Graph/Edge interface for MongoDB,
providing a similar set of commands,
etc. Uses MongoAlchemy.
"""

from base_model import BaseNode, BaseEdge
from mongoalchemy.fields import ( 
        ObjectIDField, StringField, NumberField, BoolField,
        computed_field, ListField)
from mongoalchemy.document import Document

# Still TODO: figure out how to get a query object from the class/self
# so that can get source/target/in_edges/out_edges, etc. Not 100% sure
# how to do this

class Node(Document, BaseNode):
    in_edge_ids = ListField(ObjectIDField)
    out_edge_ids = ListField(ObjectIDField)
    @computed_field(deps=[out_edge_ids])
    def out_edges(self, ids):
        """ generator for edges going out of the Node """
        pass
    @computed_field(deps=[in_edge_ids])
    def in_edges(self, ids):
        """ generator for edges directed into the Node """
        pass
    @property
    def edges(self):
        """ generator for edges (first yields in_edges, then out_edges"""
        for edge in self.in_edges:
            yield edge
        for edge in self.out_edges:
            yield edge
    @property
    def id(self):
        return self.mongo_id

class Edge(Document, BaseEdge):
    label = StringField()
    size = NumberField()
    color = StringField(max_length=BaseEdge.COLORLENGTH)
    source_id = ObjectIDField(required=True)
    target_id = ObjectIDField(required=True)
    directed = BoolField()

    @computed_field(one_time=True, deps=[source_id])
    def _source(self):
        return obj.get("source_id", "")

    @computed_field(one_time=True, deps=[target_id])
    def _target(self):
        return obj.get("target_id", "")

    @property
    def source(self):
        """ source Node """
        return self._source

    @source.setter
    def source(self, node):
        self.source_id = node.id

    @property
    def target(self):
        """ target Node """
        return self._target

    @target.setter
    def target(self, node):
        self.target_id = node.id
    # @computed_field(one_time=True, deps=[source_id])
    # def source(self, source_id):
    #     pass
    # @computed_field(one_time=True, deps=[target_id])
    # def target(self):
    #     pass
    @property
    def id(self):
        return self.mongo_id

def create_base_classes():
    """ included just to assure parity between sql_models and mongo_models.
    Currently doesn't do anything (just returns Node, Edge). May do so in the
    future """
    return Node, Edge
