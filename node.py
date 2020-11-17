import collections
import binarytree

class Node:
    def __init__(self, left=None, left_length=0, right=None, right_length=0, parent=None):
        self.left, self.right, self.max, self.min, self.parent = left, right, None, None, parent
        self.left_length, self.right_length = left_length, right_length

    def __str__(self):
        return self.convert_binarytree().__str__()

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

    def insert(self, node, left):
        if left is True:
            self.left = node
            self.left_length = 1
        else:
            self.right = node
            self.right_length = 1

        node.parent = self
        child = node
        parent = self
        while parent is not None:
            parent.max = max(parent.max, child.max) if \
            (child.max is not None and parent.max is not None) else \
                (parent.max if parent.max is not None else child.max)
            parent.min = min(parent.min, child.min) if \
            (child.min is not None and parent.min is not None) else \
                (parent.min if parent.min is not None else child.min)
            child = parent
            parent = parent.parent

        return node
    
    def encode(self, data):
        if data > self.max or data < self.min:
            print(repr(data) + "doesn't exist in the tree")
            return ""
        else:    
            if self.left is not None and self.left.max is not None and self.left.max >= data:
                return "0" + self.left.encode(data)
            if self.right is not None and self.right.min is not None and self.right.min <= data:
                return "1" + self.right.encode(data)

    def find_node(self, data):
        if data > self.max or data < self.min:
            print(repr(data) + " doesn't exist in the tree")
            return None
        else:
            if self.left is not None and self.left.max is not None and self.left.max >= data:
                return self.left.find_node(data)
            if self.right is not None and self.right.min is not None and self.right.min <= data:
                return self.right.find_node(data)
    
    def find_all_depth(self):
        ret = {}
        if self.left is not None:
            ret.update({data : key+1 for data, key in self.left.find_all_depth().items()})
        if self.right is not None:
            ret.update({data : key+1 for data, key in self.right.find_all_depth().items()})
        return ret

    def find_depth(self):
        if self.has_parent():
            return self.parent.find_depth()+1
        else:
            return 0

    def has_parent(self):
        return self.parent is not None
    
    def has_child(self, left):
        if left:
            return self.left is not None
        else:
            return self.right is not None
    
    def replace(self, node):
        if self.has_parent():
            self.parent.insert(node, self.parent.left is self)

    def reduce_edge_length_by(self, reduction):
        ret = 0
        if self.parent.left is self:
            ret = min(self.parent.left_length-1, reduction)
            self.parent.left_length -= ret
        else:
            ret = min(self.parent.right_length-1, reduction)
            self.parent.right_length -= ret
        return ret

    def find_ancestor(self, generation):
        cur = self
        for _ in range(generation):
            cur = cur.parent
        return cur

    def find_parent(self):
        if self.parent is not None:
            return self.parent
        else:
            print("no parent found")

    def convert_binarytree(self):
        this = binarytree.Node(0)
        if self.left is not None:
            this.left = self.left.convert_binarytree()
        if self.right is not None:
            this.right = self.right.convert_binarytree()
        return this

    @staticmethod
    def rebuild(location):
        root = Node()
        for data, direction in location.items():
            cur = root
            for is_left in direction[:-1]:
                if cur.has_child(is_left):
                    cur = cur.left if is_left else cur.right
                else:
                    cur = cur.insert(Node(), is_left)
            cur.insert(LeafNode(data), direction[-1])
        return root

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

    def encode(self, data):
        return ""

    def find_all_depth(self):
        return {self.data : 0}
        
    def find_node(self, data):
        if data is self.data:
            return self
        else:
            print("node not found")
            return None

    def convert_binarytree(self):
        return binarytree.Node(self.data)