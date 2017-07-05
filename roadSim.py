import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import simpy, cv2, sys, os

from Simulation import *
from statistics import *

plt.style.use('ggplot')

def road():
    env = simpy.Environment()
    # env = simpy.rt.RealtimeEnvironment(factor=0.8)
    img = np.zeros((400, 400, 3), dtype=np.uint8)
    sim = Simulation(env, img)
    c = ((np.float32(100.), np.float32(200.)), (np.float32(300.), np.float32(200.)))
    sim.network.addLink(
        linkID=1,
        turns={'exit': 1.},
        type='link',
        length=20,
        t0=1,
        MU=1,
        coordinates=c
    )

    # draw link on map
    sim.networkLines.append(c)

    # initialize car generation
    env.process(sim.source(10, LAMBDA=1, linkid=1))

    # draw initial network
    for i in sim.networkLines:
        cv2.line(sim.img, i[0], i[1], (255,255,255), 3)
    name = 'Single Road'
    cv2.imshow(name, sim.img)

    # start visualization update process
    env.process(sim.visualization(frequency=0.2, name=name))

    # wait for keypress to start simulation
    print('press space to start')
    k = cv2.waitKey(0)
    if k == 27:
        sys.exit()
    # run simulation
    env.run()

    print('Press any key to exit')
    cv2.waitKey(0)

if __name__ == '__main__':
    road()
