# Encoded-media check — 364

The actual new MP4 decoded successfully:106frames,24/1fps,432×768,H.264,
yuv420p, faststart, one video stream and no audio. Duration106/24=4.4167s.
The leader shot is276..333 with24 actual context frames before and after.
No frame interpolation, player speed change, hold duplication or music retime.

Actual decoded samples at indices0,23,24,31,39,48,54,62,65,74,75,76,81,82,
101,102,105 were inspected (encoded-samples.json and decoded/samples.jpg).
They cover both cuts, slam, gather, rise, crest, descent, consecutive arrivals,
recovery and last context cut. No blank frame, inversion, unexpected crop,
colour jump or encode-specific layer defect was identified. All16 repeated
source314 controls have zero changed colour channels.

These are decoded still/timed samples, not direct playback or listening.
AV313 remains pending. This export does not prove that mobile app transport or
the earlier grey-box issue is fixed. No S3 upload was made.
