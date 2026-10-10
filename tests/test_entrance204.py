import importlib.util
from pathlib import Path
import numpy as np
spec=importlib.util.spec_from_file_location('story',Path(__file__).parents[1]/'scripts/entrance204_story.py');story=importlib.util.module_from_spec(spec);spec.loader.exec_module(story)
def test_clock_monotone_and_no_freeze():
 t=np.linspace(0,10,2401);s=np.array([story.source_time(x) for x in t]);assert s[0]==0 and s[-1]==8;assert np.diff(s).min()>0;assert np.gradient(s,t).min()>.25
def test_glance_is_not_ending():
 assert story.glance(5)==0 and story.glance(6)>.9;assert story.glance(7.2)==0 and story.glance(8)==0
def test_recognition_perceptible_controls():
 a=story.face_values(0,True);b=story.face_values(1.5,True);assert b['browDownLeft']-a['browDownLeft']>.15;assert b['mouthPressLeft']>a['mouthPressLeft'];assert all(0<=v<=1 for v in b.values())
def test_whole_edit_and_forward_ending():
 rows=[story.shot_frame(i) for i in range(432)]
 assert rows[0]==('opening','opening',217.) and rows[143][2]==360
 assert rows[144]==('recognition','recognition',289.)
 assert rows[192]==('route','ots',361.) and rows[-1]==('route','final',553.)
 assert all(b[2]>a[2] for a,b in zip(rows[192:-1],rows[193:]))
 assert all(story.glance((r[2]-361)/24)==0 for r in rows[-18:])

contact_spec=importlib.util.spec_from_file_location('contact',Path(__file__).parents[1]/'scripts/entrance204_contact.py');contact=importlib.util.module_from_spec(contact_spec);contact_spec.loader.exec_module(contact)
def test_contact_fixed_offset_leaves_roots_and_clear_guides():
 centers=np.zeros((2,2,12,3));centers[:,0,:,0]=1.;centers[:,1,:,0]=-1.;centers[:,:,0,1]=10
 hands=np.array([[[1,0,0],[-1,0,0]]]*2,dtype=float)
 shift,report=contact.offsets(centers,hands)
 assert np.all(shift[:,0]==0) and report['hand_proxy_intersections_after']==0
 assert np.all(shift[0,1:]>=.799) and np.all(shift[1,1:]<=-.799)
def test_contact_rejects_nonfinite():
 import pytest
 with pytest.raises(ValueError):contact.offsets(np.full((1,1,12,3),np.nan),np.zeros((1,2,3)))
