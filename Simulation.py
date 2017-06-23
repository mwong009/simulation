import numpy as np
from numpy.random import multinomial
from distribution import normal, uniform
import simpy

from RoadNetwork import *

class Simulation(object):
    def __init__(self, env):
        self.env = env
        self.data = []
        self.network = RoadNetwork(env)
        self.carCounter = 0

    def car(self, carID, t_arrival, node, turn_ratio, linkid):
        """ car generator """
        t_entry, t_travel = t_arrival
        queue = self.network.links[linkid]['queue']
        yield self.env.timeout(t_travel) # en-route
        yield queue.put(1) # put 1 car in link queue
        with node.request() as req:
            q_length = queue.level # query queue length
            print('car %d arrived on link %s at %.2fs (Q=%d cars) ' % (carID, linkid, sum(t_arrival), q_length))
            self.data.append((carID, linkid, 'arrival', sum(t_arrival), q_length))

            result = yield req # wait until queue is ready
            t_service = exponential(self.network.links[linkid]['mu'])

            if node in self.network.trafficLights: # query traffic lights if available
                tg = self.network.trafficLights[node]
                with tg.stop.request(priority=0) as stop:
                    yield stop # yield to traffic light 'stop'

            yield self.env.timeout(t_service) # services at junction
            t_depart = self.env.now # departure time
            t_queue = t_depart - sum(t_arrival) # time spent in queue

            # recursions (move 'car' into next link with probability prob)
            prob = list(turn_ratio.values())
            egress = list(turn_ratio.keys())[np.argmax(multinomial(1, prob))]
            if egress is not 'exit' and egress in self.network.links.keys():
                c = self.car(carID=carID,
                    t_arrival=(t_depart, exponential(self.network.links[egress]['t0'])),
                    node=self.network.links[egress]['node'],
                    turn_ratio=self.network.links[egress]['turns'],
                    linkid=egress)
                self.env.process(c)

        yield queue.get(1)
        q_length = queue.level
        print('car %d departed link %s at %.2fs (Q=%d cars)' % (carID, linkid, t_depart, q_length))
        self.data.append((carID, linkid, 'departure',  t_depart, q_length, t_queue))

    def source(self, demand_duration, LAMBDA, linkid):
        """ Event generator """
        if linkid not in self.network.links.keys():
            print('Link %s not defined, exiting simulation' % linkid)
            exit()
        while self.env.now < demand_duration:
            arrival_rate = exponential(LAMBDA)
            #print('arrival rate', arrival_rate)
            turn_ratio = self.network.links[linkid]['turns']
            n = self.network.links[linkid]['node']
            t_entry = self.env.now
            t_travel = uniform(0, self.network.links[linkid]['t0'])
            t_arrival = (t_entry, t_travel)

            self.carCounter +=1
            self.data.append((self.carCounter, linkid, 'entry', t_entry, None, None))
            c = self.car(self.carCounter, t_arrival, n, turn_ratio, linkid)
            self.env.process(c)
            yield self.env.timeout(arrival_rate)
