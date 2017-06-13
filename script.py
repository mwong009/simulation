import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import simpy
import sys, os

from Simulation import *

plt.style.use('ggplot')


def main():
    #env = simpy.Environment()
    env = simpy.rt.RealtimeEnvironment(factor=0.2)

    sim = Simulation(env)
    sim.network.addLink(linkID='1E', turns={'3S': 0.25, '4E': 0.5}, nodeID='1a', t0=1, mu=1)
    sim.network.addLink(linkID='1W', turns={}, nodeID='1b', t0=1, mu=0)

    sim.network.addLink(linkID='2S', turns={'3S': 0.5, '4E': 0.25}, nodeID='2a', t0=1, mu=1)
    sim.network.addLink(linkID='2N', turns={}, nodeID='2b', t0=1, mu=0)

    sim.network.addLink(linkID='3N', turns={'2N': 0.5, '4E':0.25}, nodeID='3a', t0=1, mu=1)
    sim.network.addLink(linkID='3S', turns={}, nodeID='3b', t0=1, mu=0)

    sim.network.addLink(linkID='4W', turns={'1W': 0.5, '2N': 0.25}, nodeID='4a', t0=1, mu=1)
    sim.network.addLink(linkID='4E', turns={}, nodeID='4b', t0=1, mu=0)

    env.process(sim.source(25, _lambda=1, linkid='1E'))
    env.process(sim.source(25, _lambda=1, linkid='2S'))
    env.process(sim.source(25, _lambda=1, linkid='3N'))
    env.process(sim.source(25, _lambda=1, linkid='4W'))
    env.run()

    ######################################
    # simulation statistics and graphing #
    ######################################
    df = pd.DataFrame(sorted(sim.data, key=lambda x: x[3]), columns=['carID', 'link', 'event', 'time', 'queue', 't_queue'])
    print(df)

    totalTravelTime = (df[['carID', 'time']].groupby(['carID']).max()- df[['carID', 'time']].groupby(['carID']).min()) #.columns = ['totalTravelTime']
    totalTravelTime.columns= ['totalTravelTime']

    totalSegments = df.loc[df['event'] == 'arrival'][['carID', 'link']].groupby(['carID']).count()
    totalSegments.columns = ['totalSegments']

    meanWaitTime = df.loc[df['event'] == 'departure'][['carID', 't_queue']].groupby(['carID']).mean()
    meanWaitTime.columns = ['meanWaitTime']

    statistics = pd.concat([totalTravelTime, totalSegments, meanWaitTime], axis=1)
    print(statistics)
    plt.figure(1)
    plt.hist(statistics['meanWaitTime'])
    plt.title('Queue time distribution')
    plt.ylabel('')
    plt.xlabel('mean waiting time (s)')
    # print(totalTravelTime)
    # print(nLinkSegments)
    plt.figure(2)
    for link in sim.network.links.keys():
        df2 = df.loc[(df['link'] == link) & (df['event'] != 'entry')]
        if df2.empty is False and df2['t_queue'].sum() > 0.:
            plt.plot(df2[['time']], df2[['queue']], label='link %s' % link)

    plt.title('Queueing Simulation')
    plt.ylabel('queue length')
    plt.xlabel('time (s)')
    plt.legend()
    plt.show()


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
  main()
