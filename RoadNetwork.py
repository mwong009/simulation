import simpy
import random, string
from numpy.random import uniform, exponential

class RoadNetwork(object):
    def __init__(self, env):
        self.env = env
        self.links = {}
        self.nodes = {}
        self.trafficLights = {}

    def addLink(self, linkID=None, turns={}, type='link', length=0, t0=1, mu=1, nodeID=None):
        if linkID in self.links:
            print('Error: Link %d has already been defined!' % linkID)
        else:
            if 'exit' not in turns.values():
                turns['exit'] = 1 - sum(turns.values())

            self.links[linkID] = {'length': length, 'turns': turns, 't0': t0, 'mu': mu}
            if nodeID is None:
                chars = string.ascii_uppercase + string.digits
                nodeID = ''.join([random.choice(chars) for i in range(8)])
            if nodeID not in self.nodes.keys():
                self.addNode(nodeID, cap=1)

            self.links[linkID]['node'] = self.nodes[nodeID]
            print('Created link %s at node %s' % (linkID, nodeID))

    def addNode(self, nodeID, cap=1):
        if nodeID in self.nodes:
            print('Error: Node %d has already been defined!' % nodeID)
        else:
            node = simpy.Resource(self.env, capacity=cap)
            self.nodes[nodeID] = node

    def addTrafficLight(self, nodeID, duration=60, sync=None, r=5, g=5, y=1):
        if nodeID in self.nodes:
            t1 = TrafficLight(self.env, duration, r, g, y)
            if sync is not None and self.nodes[sync] in self.trafficLights:
                t2 = self.trafficLights[self.nodes[sync]]
                t1.setStatus(t2.status)
                t1.setTimings((t2.t_red, t2.t_green, t2.t_amber))
            self.trafficLights[self.nodes[nodeID]]= t1
            # to interrupt the traffic light, call tl.process.interrupt()
            print('Created traffic light at node %s' % (nodeID))
        else:
            print('Node %s not found!' % nodeID)
            exit()

class TrafficLight(object):
    def __init__(self, env, t_max=50, t_red=5, t_green=5, t_amber=1):
        self.env = env
        self.t_red = t_red
        self.t_green = t_green
        self.t_amber = t_amber
        self.status = random.choice(['GREEN', 'RED'])
        self.process = env.process(self.cycle(t_max))
        self.stop = simpy.PriorityResource(env, capacity=1)

    def setStatus(self, color):
        self.status = color

    def setTimings(self, timings):
        self.t_red, self.t_green, self.t_amber = timings

    def cycle(self, t_max):
        while self.env.now < t_max:
            if self.status == 'RED':
                with self.stop.request(priority=-1): # all cars must yield to 'RED'
                    print('Light is %s at %.2f' %  (self.status, self.env.now))
                    try:
                        yield self.env.timeout(self.t_red)
                    except simpy.Interrupt:
                        pass
                    self.status = 'AMBER'
                    self.prev_status = 'RED'
            if self.status == 'GREEN':
                print('Light is %s at %.2f' %  (self.status, self.env.now))
                try:
                    yield self.env.timeout(self.t_green)
                except simpy.Interrupt:
                    pass
                self.status = 'AMBER'
                self.prev_status = 'GREEN'
            if self.status == 'AMBER':
                with self.stop.request(priority=1): # allow cars in intersection to continue
                    print('Light is %s at %.2f' %  (self.status, self.env.now))
                    yield self.env.timeout(self.t_amber)
                    try:
                        self.prev_status
                    except AttributeError:
                        self.prev_status = random.choice(['GREEN', 'RED'])
                    if self.prev_status == 'GREEN':
                        self.status = 'RED'
                    elif self.prev_status == 'RED':
                        self.status = 'GREEN'
