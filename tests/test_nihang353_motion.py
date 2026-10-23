from movie_factory.adapters.blender.nihang_motion353 import curl_angle

def test_crest_has_compact_curl_and_landing_is_exact():
 assert curl_angle(327,1)==.75
 assert 0<curl_angle(336,.9)<curl_angle(331,1)
 assert all(curl_angle(f,1)==0 for f in range(341,442))
 assert curl_angle(290,0)==0

def test_curl_is_bounded():
 assert all(0<=curl_angle(f,k)<=.75 for f in range(252,442) for k in (-1,0,.2,.5,1,2))
