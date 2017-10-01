simulation
==========


Requriements
------------
Python (3.5+) https://www.python.org/downloads/

NumPy (1.13) https://scipy.org/install.html

Matplotlib (2.02) https://matplotlib.org/

SimPy (3.0.10) https://simpy.readthedocs.io/

opencv (3.0+) http://www.opencv.org/

    > sudo apt-get install python3 python3-dev python3-tkinter pip3
    > sudo pip3 install numpy scipy matplotlib opencv-python

Usage and Documentation
-----------------------
SimPy is a process-based discrete-event simulation framework based on standard Python. Processes in SimPy are defined by Python generator functions and may, for example, be used to model active components like customers, vehicles or agents. SimPy also provides various types of shared resources to model limited capacity congestion points (like servers, checkout counters and tunnels).

From this directory, run the command:

    > python3 script.py

Sample output:

    car 1 arrived on link 1E at 0.03s (Q=0)
    car 2 arrived on link 2S at 0.63s (Q=0)
    car 3 arrived on link 6N at 0.73s (Q=0)
    ...
    car 1 departed link 4E at 1.29s (Q=0)
    car 6 arrived on link 6N at 1.71s (Q=0)
    car 6 departed link 6N at 1.83s (Q=0)
    ...
    car 96 arrived on link 7E at 37.20s (Q=0)
    car 96 departed link 7E at 37.20s (Q=0)
    car 99 departed link 6N at 38.10s (Q=0)
    car 99 arrived on link 7E at 39.06s (Q=0)
    car 99 departed link 7E at 39.06s (Q=0)

Statistics can be generated

    [514 rows x 6 columns]
           totalTravelTime  totalSegments  meanWaitTime
    carID                                              
    1             3.759368              3      0.372207
    2             7.340689              3      1.282778
    3             2.007794              2      0.064265
    4             1.956925              1      1.140182
    5             5.664470              3      0.986793
    6             1.404893              2      0.055849
    7             4.237412              1      3.289740
    8             3.490860              1      3.139994
    9             2.345139              1      1.451333
    10            4.175994              1      3.244251
    11            7.098955              3      1.487988
    ...

Plotting done on Matplotlib
