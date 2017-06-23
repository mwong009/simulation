import pandas as pd
import numpy as np

def meanQueueLength(plt, data):
    mql = data.loc[data['event'] == 'departure'][['link', 'queue']].groupby(['link']).mean()
    vql = data.loc[data['event'] == 'departure'][['link', 'queue']].groupby(['link']).var()
    mql.plot.bar(yerr=np.sqrt(vql))

    mql.columns=['mean']
    vql.columns=['variance']
    print(pd.concat([mql, vql], axis=1))

    plt.title('Mean Queue Length')
    plt.ylabel('length (cars)')
    plt.xlabel('Link ID')
