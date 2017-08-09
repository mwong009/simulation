import sys
import simpy
import cv2
import timeit
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import simulation

import simulation.statistics as stats
from simulation.roadnetwork import RoadNetwork
from simulation.simulation import Simulation
from simulation.siouxfalls import SiouxFalls

plt.style.use('ggplot')

class Bootstrap(object):
    def __init__(self, env):
        self.env = env

        # create simulation enviromment
        img = np.zeros((900, 800, 3), dtype=np.uint8)
        self.sim = Simulation(self.env, img)

    def processSimulation(self):
        # initialize Sioux Falls network
        siouxfalls = SiouxFalls(0.0025)

        # create Sioux Fall network by enumerating across all links
        for linkid, t0 in enumerate(siouxfalls.t0):

            # calculate length of link with sqrt((x1 - x2)^2 + (y1 - y2)^2)
            length = np.sqrt(
                np.power(siouxfalls.x1[linkid] - siouxfalls.x2[linkid], 2)
              + np.power(siouxfalls.y1[linkid] - siouxfalls.y2[linkid], 2)) / 600.
            mu = siouxfalls.mu[linkid]

            # assign nodeID to each link if check pass in node list
            for i, node in enumerate(siouxfalls.nodes):
                if linkid+1 in node:
                    nodeID = i

            # assign turn ratio to each link
            turns = {}
            for j, turn in enumerate(siouxfalls.turns[linkid]):
                turns[j + 1] = turn

            # assign exit probability from last item in turn list ([-1])
            turns['exit'] = turns.pop(list(turns.keys())[-1])

            # generate coordinates of each link (for visualization)
            pt1 = (np.float32(siouxfalls.x1[linkid] / 600.),
                   np.float32(siouxfalls.y1[linkid] / 600.))

            pt2 = (np.float32(siouxfalls.x2[linkid] / 600.),
                   np.float32(siouxfalls.y2[linkid] / 600.))

            c = (pt1, pt2)

            # draw link on map
            self.sim.networkLines.append(c)

            # add link to sim.network
            self.sim.network.addLink(linkID=linkid+1, turns=turns,
                                type='link',  length=length,
                                t0=t0, MU=mu, nodeID=nodeID,
                                coordinates=c)

            # initialize car generation
            self.env.process(self.sim.source(
                10, LAMBDA=siouxfalls.flambda[linkid], linkid=linkid+1))

        yield self.env.timeout(1)

def main():

    name = 'Sioux Falls Network'

    ########################
    # bootstrap parameters #
    ########################
    boot = 5

    #################################
    # initialize discrete event env #
    #################################
    env = simpy.Environment()  # use instant simulation
    # env = simpy.rt.RealtimeEnvironment(factor=1.)  # use real time simulation

    # setup simulation processes
    bsProcess = []
    for b in range(boot):
        bs = Bootstrap(env)
        env.process(bs.processSimulation())
        bsProcess.append(bs)

    start_time = timeit.default_timer() # start simulation timer

    env.run()

    end_time = timeit.default_timer() # end simulation timer

    # compile simulation statistics
    bsTable = None
    for n, bootstrap in enumerate(bsProcess):
        df = pd.DataFrame(sorted(bootstrap.sim.data, key=lambda x: x[3]),
                          columns=['carID', 'link', 'event',
                                   'time', 'queue', 't_queue'])

        meanQlength = df.loc[df['event'] == 'departure'][
            ['link', 'queue']].groupby(['link']).mean()
        meanQlength.columns=['mean']

        varQlength = df.loc[df['event'] == 'departure'][
            ['link', 'queue']].groupby(['link']).var()
        varQlength.columns=['variance']

        maxQlength = df.loc[df['event'] == 'departure'][
            ['link', 'queue']].groupby(['link']).max()
        maxQlength.columns=['max']

        if bsTable is None:
            bsTable = maxQlength
            bsTable.columns = [1]

        else:
            bsTable[n+1] = maxQlength

    mean = bsTable.mean(axis=1)
    mse = bsTable.var(axis=1, ddof=0)
    bsTable['mean'] = mean
    bsTable['MSE'] = mse

    print('Simulation runtime: %.3fs' % (end_time-start_time))

    with pd.option_context('expand_frame_repr', False):
        print(bsTable)

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
  main()
