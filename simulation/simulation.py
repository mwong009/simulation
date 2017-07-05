import simpy
import cv2
import numpy as np
from numpy.random import multinomial

from simulation.distribution import uniform
from simulation.roadnetwork import RoadNetwork


class Simulation(object):
    def __init__(self, env, img):
        self.env = env
        self.data = []
        self.network = RoadNetwork(env)
        self.carCounter = 0
        self.carsInSystem = 0
        self.t_max = 0
        self.img = img
        self.networkLines = []

    def visualization(self, frequency, name):
        """ visualization env process """
        while self.env.now < self.t_max or self.carsInSystem > 0:
            # redraw entire network
            for i in self.networkLines:
                cv2.line(self.img, i[0], i[1], (255,255,255), 3)
            for _linkid in self.network.links:
                if 'queueLines' in self.network.links[_linkid]:
                    line = self.network.links[_linkid]['queueLines']
                    cap = self.network.links[_linkid]['capacity']
                    # overlay = self.img.copy()
                    cv2.line(self.img, line[0], line[1], (0,0, 255), 3)
                    # opacity = 0.8
                    # cv2.addWeighted(overlay, opacity, self.img, 1-opacity, 0, self.img)

            cv2.imshow(name, self.img)
            k = cv2.waitKey(1)
            yield self.env.timeout(frequency)

    def updateQueue(self, queue, linkid, carLength=1.):
        # draw queue lines
        length = self.network.links[linkid]['length']
        pt1 = self.network.links[linkid]['coordinates'][0]
        pt2 = self.network.links[linkid]['coordinates'][1]

        # coordinate math
        dk = np.min((1, queue.level * carLength/length))
        x2 = pt2[0] + dk * (pt1[0] - pt2[0])
        y2 = pt2[1] + dk * (pt1[1] - pt2[1])
        pt1 = (np.float32(x2), np.float32(y2))
        line = (pt2, pt1)

        # add to data dictionary
        self.network.links[linkid]['queueLines'] = line
        self.network.links[linkid]['capacity'] = dk

    def car(self, carID, t_arrival, node, turn_ratio, linkid):
        """ car generator """

        # prepare variables
        t_entry, t_travel = t_arrival
        queue = self.network.links[linkid]['queue']

        # en-route
        yield self.env.timeout(t_travel)

        # put 1 car in link queue
        yield queue.put(1)

        # update queue length for visualization
        self.updateQueue(queue, linkid)

        # query queue length
        with node.request() as req:
            q_length = queue.level

            # data logging
            print('car %d arrived on link %s at %.2fs (Q=%d cars) ' % (carID, linkid, sum(t_arrival), q_length))
            self.data.append((carID, linkid, 'arrival', sum(t_arrival), q_length))

            # wait until queue is ready
            result = yield req
            t_service = exponential(self.network.links[linkid]['MU'])

            # query traffic lights if available
            if node in self.network.trafficLights:
                tg = self.network.trafficLights[node]

                # yield to traffic light 'stop'
                with tg.stop.request(priority=0) as stop:
                    yield stop

            # services at junction
            yield self.env.timeout(t_service)

            # time spent in queue
            t_depart = self.env.now
            t_queue = t_depart - sum(t_arrival)

            # recursions (move 'car' into next link with probability prob)
            prob = list(turn_ratio.values())
            egress = list(turn_ratio.keys())[np.argmax(multinomial(1, prob))]
            if egress is not 'exit' and egress in self.network.links.keys():
                c = self.car(
                    carID=carID,
                    t_arrival=(t_depart, exponential(self.network.links[egress]['t0'])),
                    node=self.network.links[egress]['node'],
                    turn_ratio=self.network.links[egress]['turns'],
                    linkid=egress
                )
                self.env.process(c)

            # keep track of the number of cars in the system
            if egress is 'exit':
                self.carsInSystem -= 1

        # release 1 car from queue
        yield queue.get(1)

        # update queue length for visualization
        self.updateQueue(queue, linkid)

        # update queue level
        q_length = queue.level

        # data logging
        print('car %d departed link %s at %.2fs (Q=%d cars)' % (carID, linkid, t_depart, q_length))
        self.data.append((carID, linkid, 'departure',  t_depart, q_length, t_queue))

    def source(self, demand_duration, LAMBDA, linkid):
        """ Event generator """
        if self.t_max < demand_duration:
            self.t_max = demand_duration
        if linkid not in self.network.links.keys():
            print('Link %s not defined, exiting simulation' % linkid)
            exit()
        while self.env.now < demand_duration:
            arrival_rate = exponential(LAMBDA)
            turn_ratio = self.network.links[linkid]['turns']
            n = self.network.links[linkid]['node']
            t_entry = self.env.now
            t_travel = uniform(0, self.network.links[linkid]['t0'])
            t_arrival = (t_entry, t_travel)

            self.carCounter +=1
            self.carsInSystem +=1
            self.data.append((self.carCounter, linkid, 'entry', t_entry, None, None))
            c = self.car(
                carID=self.carCounter,
                t_arrival=t_arrival,
                node=n,
                turn_ratio=turn_ratio,
                linkid=linkid
            )
            self.env.process(c)
            yield self.env.timeout(arrival_rate)
