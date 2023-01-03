import os
import math
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import json

############## Configuration ##############

numOfPlots = 50
minPlayDurationMS = 60000
outDir = 'out'
inDir = 'extended_history'

############################################

def toDate(s):
    d = datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').date()
    d -= timedelta(days=(d.day-1))
    return d

def getAlbum(song):
    al = song["master_metadata_album_album_name"]
    ar = song["master_metadata_album_artist_name"]
    return  f"{ar} – {al}"

def getSong(song):
    al = song["master_metadata_album_album_name"]
    ar = song["master_metadata_album_artist_name"]
    ti = song["master_metadata_track_name"]
    song = f"{ar} – {al} – {ti}"
    return song

def getArtist(song):
    return song["master_metadata_album_artist_name"]


def getPlot(data, name):
    print(f"Creating analysis for {name}")
    df = pd.DataFrame(data=data, columns=['descriptor', 'date', 'count'])
    # df = df[df['date'] > datetime.fromisoformat('2017-10-01').date() ]
    df = pd.pivot_table(df, index='descriptor', columns='date', values='count', aggfunc='count').fillna(0)
    counts = list(df.sum(axis=1))
    minCount = 0
    if len(counts) > numOfPlots:
        counts.sort(reverse=True)
        minCount = counts[numOfPlots]
    df = df.loc[df.sum(axis=1) > minCount]
    df = df.transpose()
    minDate = df.loc[df.sum(axis=1) > 0].index.min()
    df = df.loc[df.index >= minDate]
    maxValue = df.max(axis=1).max()
    
    print(f"Creating plot for {name}")
    plt.rcParams.update({'font.size': 6}) 
    df.plot(
        subplots=True,
        layout=(math.ceil(1.0*df.shape[1]/2),2),
        ylim=(0,maxValue),
        )
    plt.subplots_adjust(left=0.05, right=0.99, top=0.95, bottom=0.1, wspace=0.1)
    plt.gcf().set_size_inches(15, 10)
    plt.suptitle(name)
    plt.savefig(f"{outDir}/{name}.png", dpi=300, bbox_inches='tight')
    print(f"Saved plot for {name} to {outDir}/{name}.png")

if __name__ == '__main__':
    inFiles = os.listdir(inDir)
    inFiles = [e for e in inFiles if e.startswith("endsong")]

    r = []
    for f in inFiles:
        print(f"Loading data from {inDir}/{f}")
        with open(f"{inDir}/{f}", "r") as fd:
            r += json.loads(fd.read())

    print(f"Loaded a total of {len(r)} songs entries")

    if not os.path.exists(outDir):
        print(f"Creating output directory {outDir}")
        os.makedirs(outDir)

    r = [e for e in r if e["ms_played"] > minPlayDurationMS]

    print(f"After filtering for play duration, {len(r)} songs remain")

    getPlot([[getAlbum(s), toDate(s['ts']), 1] for s in r], 'albums')
    getPlot([[getSong(s), toDate(s['ts']), 1] for s in r], 'songs')
    getPlot([[getArtist(s), toDate(s['ts']), 1] for s in r], 'artists')