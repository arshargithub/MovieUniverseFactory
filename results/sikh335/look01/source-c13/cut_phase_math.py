"""Smooth foreleg recovery reparameterization; support is unchanged."""
import math

def recovery_phase(phase, touchdown, duty, strength=.5):
    p=(phase-touchdown)%1
    if p<=duty:return phase
    u=(p-duty)/(1-duty)
    w=u+strength*(u-.5)*math.sin(math.pi*u)**2
    return phase+(w-u)*(1-duty)
