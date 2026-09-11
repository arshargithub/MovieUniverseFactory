"""Exact physical-time mapping for animation actions on a shared timeline."""
from __future__ import annotations

import math


def action_time_scale(source_fps:float,timeline_fps:float)->float:
    """Return the NLA scene-frame scale that preserves physical duration."""
    if not all(type(value) in {int,float} and math.isfinite(value) and value>0 for value in (source_fps,timeline_fps)):
        raise ValueError("Animation frame rates must be positive finite numbers")
    return timeline_fps/source_fps


def source_frame_at_timeline_frame(source_start:float,timeline_start:float,timeline_frame:float,
                                   source_fps:float,timeline_fps:float)->float:
    """Map a shared-timeline frame to the action's possibly fractional frame."""
    scale=action_time_scale(source_fps,timeline_fps)
    if not all(type(value) in {int,float} and math.isfinite(value) for value in (source_start,timeline_start,timeline_frame)):
        raise ValueError("Animation frame coordinates must be finite numbers")
    return source_start+(timeline_frame-timeline_start)/scale


def physical_duration_seconds(frame_start:float,frame_end:float,source_fps:float)->float:
    if frame_end<frame_start: raise ValueError("Animation frame range is reversed")
    action_time_scale(source_fps,source_fps)
    return (frame_end-frame_start)/source_fps
