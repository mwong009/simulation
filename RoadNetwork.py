import simpy
import random, string
from numpy.random import uniform, exponential

class RoadNetwork(object):
    def __init__(self, env):
        self.env = env
        self.links = {}
        self.nodes = {}

    def addLink(self, linkID=None, turns={}, type='link', length=0, t0=1, mu=1, nodeID=None):
        if linkID in self.links:
            print('Error: Link %d has already been defined!' % linkID)
        else:
            if 'exit' not in turns.values():
                turns['exit'] = 1 - sum(turns.values())
            self.links[linkID] = {
                'length': length,
                'turns': turns,
                't0': t0,
                'mu': mu}
            if nodeID is None:
                chars = string.ascii_uppercase + string.digits
                nodeID = ''.join([random.choice(chars) for i in range(8)])
            if nodeID not in self.nodes.keys():
                self.addNode(nodeID, cap=1)
            self.links[linkID]['node'] = self.nodes[nodeID]

    def addNode(self, nodeID, cap=1):
        if nodeID in self.nodes:
            print('Error: Node %d has already been defined!' % nodeID)
        else:
            node = simpy.Resource(self.env, capacity=cap)
            self.nodes[nodeID] = node
