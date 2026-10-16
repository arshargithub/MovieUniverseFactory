# Source provenance and license notice

`src/movie_factory/trellis_adapter/uvraster.py` adapts the barycentric sampling and paired edge-write method from `andrakis/TRELLIS.2-stableprojectorz`, revision `1481f4995870460b6442be50b6265307b6d6d07f`, `o-voxel/o_voxel/uvraster.py`. That file declares MIT. Local changes replace common-grid batching with bounded ragged candidates, deterministic source-order overlap ownership, input validation and instrumentation. Upstream source retained in `results/sikh288/upstream/` for diagnosis, not installed as a package.

Upstream official exporter/loader snapshots are from Microsoft TRELLIS.2 revision `75fbf0183001ed9876c8dbb35de6b68552ee08bd`. Both inspected repositories provide the following root notice. This notice does not license third-party dependencies or weights; the installed runtime requires its own resolved inventory. DINOv3 access/terms remain separate. Do not redistribute or execute restricted NVIDIA/BRIA components through these snapshots.

MIT License

Copyright (c) Microsoft Corporation.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
