"""Pure three-clock design for21s; route action never stretches."""
import numpy as np
PERIOD=24/2.2
def clocks(kind,index):
    if kind=='opening':
        if not 0<=index<198:raise ValueError('Opening index')
        physical=217+index-54 if index>=54 else 217+index+PERIOD*5-54
        editorial=217+float(np.interp(index,[0,72,114,198],[0,72,96,144]))
        return min(physical,360),min(editorial,360),217+index-72
    if kind=='route':
        if not 0<=index<306:raise ValueError('Route index')
        physical=361+index-18 if index>=18 else 361+(index-18)%PERIOD
        editorial=361+index*30/48 if index<48 else physical
        return physical,editorial,361+index-18
    raise ValueError('Unknown part')
