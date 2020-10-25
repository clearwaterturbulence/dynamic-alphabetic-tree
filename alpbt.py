import node
import collections
import math

class AlphabeticTree:
    def __init__(self):
        self.root = node.Node()
        self.count = collections.Counter()
        self.depth = dict()