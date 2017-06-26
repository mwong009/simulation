import simpy
import random, string
from numpy.random import uniform, exponential

class RoadNetwork(object):
    def __init__(self, env):
        self.env = env
        self.links = {}
        self.nodes = {}
        self.trafficLights = {}

    def addLink(self, linkID=None, turns={}, type='link', length=0, t0=1, MU=1, nodeID=None, coordinates=((0, 0), (0 ,0))):
        if linkID in self.links:
            print('Error: Link %d has already been defined!' % linkID)
        else:
            if 'exit' not in turns.values():
                turns['exit'] = min(1 - sum(turns.values()), 1)

            self.links[linkID] = {'length': length, 'turns': turns, 't0': t0, 'MU': MU}
            if nodeID is None:
                chars = string.ascii_uppercase + string.digits
                nodeID = ''.join([random.choice(chars) for i in range(8)])
            if nodeID not in self.nodes.keys():
                self.addNode(nodeID, cap=1)

            self.links[linkID]['node'] = self.nodes[nodeID]
            self.links[linkID]['queue'] = simpy.Container(self.env)
            self.links[linkID]['coordinates'] = coordinates
            print('Created link %s at node %s' % (linkID, nodeID))

    def addNode(self, nodeID, cap=1):
        if nodeID in self.nodes:
            print('Error: Node %d has already been defined!' % nodeID)
        else:
            node = simpy.Resource(self.env, capacity=cap)
            self.nodes[nodeID] = node

    def addTrafficLight(self, nodeID, duration=60, sync=None, t=[5, 1, 5]):
        if nodeID in self.nodes:
            t1 = TrafficLight(self.env, duration, t)
            if sync is not None and self.nodes[sync] in self.trafficLights:
                t2 = self.trafficLights[self.nodes[sync]]
                t1.setStatus(t2.status)
                t1.setTimings(list(t2.timings.values()))
            self.trafficLights[self.nodes[nodeID]]= t1
            # to interrupt the traffic light, call tl.process.interrupt()
            print('Created traffic light at node %s' % (nodeID))
        else:
            print('Node %s not found!' % nodeID)
            exit()

class TrafficLight(object):
    def __init__(self, env, t_max=50, t=[5, 1, 5]):
        self.env = env
        self.timings = {'t_red': t[0], 't_amber': t[1], 't_green': t[2]}
        self.status = random.choice(['GREEN', 'RED'])
        self.process = env.process(self.cycle(t_max))
        self.stop = simpy.PriorityResource(env, capacity=1)

    def setStatus(self, color):
        self.status = color

    def setTimings(self, t=[5, 1, 5]):
        self.timings = {'t_red': t[0], 't_amber': t[1], 't_green': t[2]}

    def cycle(self, t_max):
        while self.env.now < t_max:
            if self.status == 'RED':
                with self.stop.request(priority=-1): # all cars must yield to 'RED'
                    print('Light is %s at %.2f' %  (self.status, self.env.now))
                    try:
                        yield self.env.timeout(self.timings['t_red'])
                    except simpy.Interrupt:
                        pass
                    self.status = 'GREEN'
                    self.prev_status = 'RED'
            if self.status == 'GREEN':
                print('Light is %s at %.2f' %  (self.status, self.env.now))
                try:
                    yield self.env.timeout(self.timings['t_green'])
                except simpy.Interrupt:
                    pass
                self.status = 'AMBER'
                self.prev_status = 'GREEN'
            if self.status == 'AMBER':
                with self.stop.request(priority=0): # allow cars in intersection to continue
                    print('Light is %s at %.2f' %  (self.status, self.env.now))
                    yield self.env.timeout(self.timings['t_amber'])
                    try:
                        self.prev_status
                    except AttributeError:
                        self.prev_status = random.choice(['GREEN', 'RED'])
                    self.status = 'RED'
                    self.prev_status = 'AMBER'
