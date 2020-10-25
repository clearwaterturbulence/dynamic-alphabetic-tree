import node
import collections
import math

class AlphabeticTree:
    def __init__(self):
        self.root = node.Node()
        self.count = collections.Counter()
        self.depth = dict()

    def access(self, data):
        # check if a new data is being accessed
        # if so, create keys for it in the dictionaries
        if (not data in self.count):
            self.count[data] = 0
            self.depth[data] = None

        # calculate new count
        self.count[data] += 1

        # calculate new depth dictated
        depth_req = AlphabeticTree.half_kraft(self.count)
        violating_nodes = AlphabeticTree.find_violating_nodes(self.depth, depth_req)
        # if there are violating nodes
        # rebuild according to the depth req
        if violating_nodes:
            self.root.half_kraft_rebuild(depth_req)

    
    @staticmethod
    def half_kraft(count):
        total = sum(count.values())
        depth_req = dict()
        for key in count:
            depth_req[key] = math.ceil(math.log2(total/count[key]))+1
        return depth_req

    @staticmethod
    def find_violating_nodes(real, req):
        ret = []
        for key, value in real.items():
            if value is None or value > req[key]:
                ret += key
        return ret


