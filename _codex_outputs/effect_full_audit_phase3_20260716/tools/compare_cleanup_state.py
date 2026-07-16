#!/usr/bin/env python3
import json, sys
a=json.load(open(sys.argv[1],encoding='utf-8'))
b=json.load(open(sys.argv[2],encoding='utf-8'))
def filt(x):
    if isinstance(x,dict): return {k:filt(v) for k,v in x.items() if k not in {'timestamp','session','session_id'}}
    if isinstance(x,list): return [filt(v) for v in x]
    return x
print(json.dumps([] if filt(a)==filt(b) else {'before':filt(a),'after':filt(b)}, ensure_ascii=False, indent=2))
