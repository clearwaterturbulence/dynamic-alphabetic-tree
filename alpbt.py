import history
import node

class AlphabeticTree:
    def __init__(self):
        self.hist = history.History()
        self.root = node.Node()

    def access(self, data):
        self.hist.access(data)

    def rebuild(self):
        heights = {k : v+1 for k, v in self.hist.ceiling_of_log_inv_empirical_prob.items()}