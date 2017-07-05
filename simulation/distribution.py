import numpy as np
import matplotlib.pyplot as plt

def plot(x):
    plt.style.use('ggplot')
    plt.hist(x, bins='auto', normed=True)
    plt.show()

def uniform(low=0, high=1):
    return np.random.uniform(low, high)

def bernoulli(p):
    U = uniform()
    if u <= p:
        X = 1
    else:
        X = 0
    return X

def poisson(LAMBDA=1):
    U = uniform()
    i = 0
    p = np.exp(-LAMBDA)
    F = p
    while U >= F:
        p = (LAMBDA*p)/(i+1)
        F = F + p
        i += 1
    X = i
    return X

def exponential(LAMBDA=1):
    U = uniform()
    X = -(LAMBDA) * np.log(U)
    return X

def normal(mean=0, var=1, d_type='Box-Muller'):
    if d_type == 'Box-Muller':
        while True:
            U_1 = uniform()
            U_2 = uniform()
            V_1 = 2*U_1 -1
            V_2 = 2*U_2 -1
            S = V_1*V_1 + V_2*V_2
            if S <= 1:
                X = np.sqrt(-2*np.log(S)/S) * V_1
                return X
    else:
        while True:
            Y_1 = exponential(1)
            Y_2 = exponential(1)
            if Y_2 - (Y_1-1)*(Y_1-1) > 0:
                Y = Y_2 - (Y_1-1)*(Y_1-1)/2
                U = uniform()
                if U <= 0.5:
                    Z = Y_1
                    return mean + np.sqrt(var)*Z
                else:
                    Z = -Y_1
                    return mean + np.sqrt(var)*Z

def lognormal(mean=0, var=1, LAMBDA=1):
    N = normal()
    X = -(LAMBDA) * np.log(N)
