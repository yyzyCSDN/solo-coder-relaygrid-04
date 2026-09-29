from __future__ import annotations
from collections import defaultdict

def last_gasp_clusters(messages: list[tuple[str,float,str]], window_s: float=30.0):
    ordered=sorted(messages,key=lambda x:x[1])
    clusters=[]
    current=[]
    window_start=None
    for meter,ts,feeder in ordered:
        if window_start is None:
            window_start=ts
        if ts-window_start<=window_s:
            current.append((meter,ts,feeder))
        else:
            clusters.append(current)
            current=[(meter,ts,feeder)]
            window_start=ts
    if current:
        clusters.append(current)
    return clusters

def infer_feeder(cluster):
    counts=defaultdict(int)
    for _,_,feeder in cluster: counts[feeder]+=1
    return max(counts,key=lambda f:(counts[f],f)) if counts else None

def ping_success_ratio(results: list[bool]) -> float:
    return sum(bool(x) for x in results)/len(results) if results else 0.0
