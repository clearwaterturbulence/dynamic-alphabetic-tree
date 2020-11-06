import collections

class Node:
    def __init__(self, left=None, right=None):
        self.left, self.right, self.max, self.min = left, right, None, None

    def are_leaves_leafnodes(self):
        return (self.left is None or self.left.are_leaves_leafnodes()) and \
         (self.right is None or self.right.are_leaves_leafnodes()) and \
          (self.left is not None or self.right is not None)

    def in_order_traversal(self):
        list = []
        if self.left is not None:
            list = list + self.left.in_order_traversal()
        if self.right is not None:
            list = list + self.right.in_order_traversal()
        return list

    def insert_left(self, node):
        self.left = node
        self.max = max(self.max, self.left.max) if \
            (self.left.max is not None and self.max is not None) else \
                (self.max if self.max is not None else self.left.max)
        self.min = min(self.min, self.left.min) if \
            (self.left.min is not None and self.min is not None) else \
                (self.min if self.min is not None else self.left.min)

    def insert_right(self, node):
        self.right = node
        self.max = max(self.max, self.right.max) if \
            (self.right.max is not None and self.max is not None) else \
                (self.max if self.max is not None else self.right.max)
        self.min = min(self.min, self.right.min) if \
            (self.right.min is not None and self.min is not None) else \
                (self.min if self.min is not None else self.right.min)
    
    def encode(self, data):
        if data > self.max or data < self.min:
            print(repr(data) + "doesn't exist in the tree")
            return ""
        if self.left is not None and self.left.max is not None and self.left.max >= data:
            return "0" + self.left.encode(data)
        if self.right is not None and self.right.min is not None and self.right.min <= data:
            return "1" + self.right.encode(data)

    def half_kraft_rebuild(self, dict):
        NotImplemented


class LeafNodeChildrenError(Exception):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return repr(self.data)

class LeafNode(Node):
    def __init__(self, data):
        super().__init__()
        self.data, self.max, self.min = data, data, data
    
    def in_order_traversal(self):
        return [self.data]

    def are_leaves_leafnodes(self):
        return True

    def insert_left(self, node):
        raise(LeafNodeChildrenError(self.data))

    def insert_right(self, node):
        raise(LeafNodeChildrenError(self.data))

    def encode(self, data):
        return ""
