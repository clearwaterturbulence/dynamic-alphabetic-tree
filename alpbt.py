import node
import collections
import math
import logging
from enum import Enum
import pandas as pd
import matplotlib.pyplot as plt

class DepthAlgo(Enum):
    ORIG = 1
    AVR_ORIG = 2

class PlacementAlgo(Enum):
    ORIG = 1
    SKIP = 2

class AlphabeticTree:
    def __init__(self, size = 1024, error = 1, depth_algo = DepthAlgo.ORIG, placement_algo = PlacementAlgo.ORIG):
        logging.debug('Creating an AlphabeticTree of size %s', size)
        self.count = collections.Counter({k:1 for k in list(range(1, size+1))})
        self.depth_algo = depth_algo
        self.placement_algo = placement_algo
        self.error = error
        self.depth = AlphabeticTree.find_all_required_depth(self.count, self.depth_algo, self.error)
        self.root = node.Node.rebuild(AlphabeticTree.half_kraft(self.depth, self.placement_algo))
        self.size = size
        self.cost = dict()
        self.cost["rebuild"] = []
        self.cost["find"] = []
        self.cost["lonesome"] = []
        self.cost_df = pd.DataFrame(columns=['data', 'movement', 'rebuild_cost', 'rebuild_level', 'find_cost', 'lonesome_reduction', 'edge_reduction'])
        logging.debug('Finished creating an AlphabeticTree')

    def access(self, data):
        logging.debug('Accessing %s', repr(data))
        if (data < self.size + 1 and data > 0):
            self.count[data] += 1
            max_depth = AlphabeticTree.find_required_depth(self.count, data, self.depth_algo, self.error)
            if (max_depth < self.depth[data]):
                self.move_up(data, self.depth[data] - max_depth)
                self.cost_df.loc[len(self.cost_df)] = [data, True, 0, 0, 0, 0, 0]
            else:
                self.cost_df.loc[len(self.cost_df)] = [data, False, 0, 0, 0, 0, 0]
                logging.debug("No moving required in accessing %s", repr(data))
        logging.debug('Finished accessing %s', repr(data))

    def move_up(self, data, depth_decrease):
        logging.debug("Moving %s up by %d", repr(data), depth_decrease)
        # first, check if the node can be relocated by reducing solitary edges
        node_in_question = self.root.find_node(data)
        reduced_amount = 0
        all_required_depth = AlphabeticTree.find_all_required_depth(self.count, self.depth_algo, self.error)
        if (node_in_question.has_parent()):
            reduced_amount = node_in_question.reduce_edge_length_by(depth_decrease)
            self.depth[data] = self.depth[data] - reduced_amount
        logging.debug("Edge reduction reduced depth by %d", reduced_amount)
        self.cost_df['edge_reduction'].iat[len(self.cost_df)-1] = reduced_amount

        if (reduced_amount < depth_decrease):
            lonesome_index = node_in_question.find_length_of_lonesome_ancestor()
            lonesome_reduction = min(lonesome_index, depth_decrease - reduced_amount)
            if lonesome_reduction > 0:
                new_node = node.LeafNode(data)
                node_in_question.find_ancestor(lonesome_reduction).replace(new_node)
                reduced_amount += lonesome_reduction
                self.depth[data] = self.depth[data] - lonesome_reduction
                node_in_question = new_node
                logging.debug("Lonesome reduction reduced depth by %d", lonesome_reduction)
                self.cost["lonesome"].append(lonesome_reduction)
                self.cost_df['lonesome_reduction'].iat[len(self.cost_df)-1] = lonesome_reduction
            
        if (reduced_amount < depth_decrease):
            logging.debug("Rebuilding while accessing %s, trying to move up by %d levels", repr(data), depth_decrease-reduced_amount)
            level_delta = depth_decrease - reduced_amount+1
            rebuild_root = node_in_question.find_ancestor(level_delta)

            while sum([2**(- d + rebuild_root.find_depth()) for data, d in all_required_depth.items() if data in range(rebuild_root.min, rebuild_root.max+1)]) > 1/2:
                logging.debug("Failed to rebuild %d levels above the node, trying parent", level_delta)
                self.cost["find"].append(rebuild_root.max +1 - rebuild_root.min)
                self.cost_df['find_cost'].iat[len(self.cost_df)-1] += rebuild_root.max +1 - rebuild_root.min
                rebuild_root = rebuild_root.find_parent()
                level_delta += 1
                    
            rebuild_depth = {data : depth - rebuild_root.find_depth() for data, depth in all_required_depth.items() if data in range(rebuild_root.min, rebuild_root.max+1)}
            logging.debug("Rebuilding %d levels above with %d leaves", level_delta, rebuild_root.max +1 - rebuild_root.min)
            self.cost_df['rebuild_level'].iat[len(self.cost_df)-1] = level_delta
            self.cost["rebuild"].append(rebuild_root.max +1 - rebuild_root.min)
            self.cost_df['rebuild_cost'].iat[len(self.cost_df)-1] = rebuild_root.max +1 - rebuild_root.min
            new_sub_tree = node.Node.rebuild(AlphabeticTree.half_kraft(rebuild_depth, self.placement_algo))
            if rebuild_root.has_parent() is not True:
                self.root = new_sub_tree
            else:
                rebuild_root.replace(new_sub_tree)
            for data, value in new_sub_tree.find_all_depth().items():
                self.depth[data] = value + new_sub_tree.find_depth()

    @staticmethod
    def find_required_depth(count, data, algo, error):
        s = sum(count.values())
        l = len(count)
        if algo is DepthAlgo.ORIG:
            return math.ceil(math.log2(s/count[data]))+ error
        if algo is DepthAlgo.AVR_ORIG:
            return math.ceil(math.log2(2*s*l/(count[data]*l+s)))+ error

    @staticmethod
    def find_all_required_depth(count, algo, error):
        s = sum(count.values())
        l = len(count)
        if algo is DepthAlgo.ORIG:
            return {d : math.ceil(math.log2(s/count[d]))+ error for d in count.keys()}
        if algo is DepthAlgo.AVR_ORIG:
            return {d : math.ceil(math.log2(2*s*l/(count[d]*l+s)))+ error for d in count.keys()}

    @staticmethod
    def half_kraft(depth, algo):
        sorted_depth = collections.OrderedDict(sorted(depth.items()))
        ret = {}
        first_key, first_val = sorted_depth.popitem(False)
        ret[first_key] = [True] * first_val
        previous_location = ret[first_key]

        while (sorted_depth):
            key, val = sorted_depth.popitem(False)
            k = max([w for w in range(1,min(len(previous_location), val)+1) if previous_location[w-1] is True])
            loc = previous_location[0:k-1] + [False] + [True] * (val-k)
            ret[key] = loc if algo is PlacementAlgo.ORIG else AlphabeticTree.next_position(loc)
            previous_location = ret[key]
        
        return ret

    @staticmethod
    def next_position(pos):
        if pos[-1] is True:
            return pos[0:-1] + [False]
        else:
            return AlphabeticTree.next_position(pos[0:-1]) + [True]