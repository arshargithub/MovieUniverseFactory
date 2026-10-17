"""Bounded supporting-layer derivative; no arbitrary worker code or paths."""
import math

FRAMES = 528
CONTROLS = (1, 36, 72, 99, 130, 155, 180, 215, 245, 275, 300, 315, 335, 365, 395, 435, 460, 500, 528)
TORCHES = ((-2.8, 88, 0), (2.8, 70, 0), (-2.8, 51, 0), (2.8, 32, 0), (-2.8, 14, 0),
           (-2.75, -5.6, 0), (2.9, -.3, 0), (-3.1, -17, 0),
           (3.1, -17, 0), (8.6, -27.4, 3.19))

def validate(job):
    if type(job) is not dict or set(job) != {'operation', 'version'}:
        raise ValueError('Exact structured job required')
    if job['operation'] not in ('inspect', 'controls', 'movie', 'reopen'):
        raise ValueError('Unsupported operation')
    if type(job['version']) is not int or not 1 <= job['version'] <= 20:
        raise ValueError('Invalid version')
    return job

def flicker(t, seed):
    return 1 + .075*math.sin(t*7.7+seed) + .035*math.sin(t*15.3+seed*2.1)

def band_radius(z):
    """Broad, tapered secondary dumalla silhouette, not concentric rope tubes."""
    return .111*math.sqrt(max(.12, 1-((z-.13)/.19)**2))
