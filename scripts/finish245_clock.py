"""Independent full-rate physical motion and attention clocks for22.5s."""
import numpy as np
from finish237_clock import PERIOD, clocks as previous

def clocks(kind,index):
    if kind=='route':
        return previous(kind,index)
    if kind!='opening' or not 0<=index<234:
        raise ValueError('Closed245 clock')
    # Add90 native frames to the original144, not repeated rendered pixels.
    physical=217+index-90 if index>=90 else 217+(index-90)%PERIOD
    # Preserve237 editorial trajectory while extending the approach and
    # composed face setup. Gait never follows this slower attention clock.
    old_index=float(np.interp(index,[0,96,138,174,234],[0,72,114,138,198]))
    editorial=217+float(np.interp(old_index,[0,72,114,198],[0,72,96,144]))
    return min(physical,360),min(editorial,360),217+index-108
