"""Continuous route camera hypotheses, all positions in source metres.

Opening uses the retained native descending camera, smoothly blended into
recognition. The route has deliberate editorial coverage after recognition.
"""
import numpy as np
from entrance205_motion import sample, smooth


def glance(t):
    return float(smooth((t-5.15)/.65)*(1-smooth((t-7.05)/.85)))


def route_camera(t, head=None):
    d=sample(t);p=d['position'];yaw=d['heading']
    forward=np.array([np.sin(yaw),-np.cos(yaw),0.])
    outboard=np.array([np.cos(yaw),np.sin(yaw),0.])
    h=p+np.array([0,0,2.6]) if head is None else np.asarray(head,float)
    checkpoint=np.array([0,-66.3,1.1])
    if t<1.25:
        loc=h-forward*1.1+outboard*.18+np.array([0,0,.1])
        target=checkpoint; lens=48.;shot='ots'
    else:
        # Director205 addendum: nearby FRONT full horse, not distant guard
        # viewpoint or an orbit that hides the bank and initial steep climb.
        wide=p+forward*5.2+outboard*2.2+np.array([0,0,2.0+5.2*d['grade']])
        wide_target=p+np.array([0,0,1.35])
        # Start inboard for the lower checkpoint geography. The camera then
        # eases ahead for a side-profile glance, keeping one continuous take.
        advance=float(smooth((t-5.0)/.85))
        close=h+forward*(.8+1.4*advance)-outboard*(1.65-.45*advance)+np.array([0,0,.65])
        target_close=h+np.array([0,0,-.06])
        w=0. if t<4.6 else 1.
        loc=wide*(1-w)+close*w
        target=wide_target*(1-w)+target_close*w
        lens=44*(1-w)+28*w;shot='front_maneuver' if not w else 'close_climb_glance_forward'
        # The final forward continuation gets a clear face-level hold rather
        # than finishing on the checking glance or an editorial freeze.
        settle=float(smooth((t-7.9)/1.0))
        # Keep the final face clear of the horse's ears/forehead: a close
        # three-quarter tracking view, not a lens directly behind its head.
        loc+=(-forward*.95-outboard*.35+np.array([0,0,.15]))*settle
        lens+=14*settle
    return loc,target,lens,shot
