import collections
import math

class History:
    def __init__(self):
        self.seq = []
        self.count = collections.Counter()
        self.ceiling_of_log_inv_empirical_prob = dict()

    def access(self, data):
        self.seq.append(data)
        self.count[data] += 1
        total = sum(self.count.values())
        for key in iter(self.count):
            self.ceiling_of_log_inv_empirical_prob[key] = math.ceil(math.log2(total/self.count[key]))
