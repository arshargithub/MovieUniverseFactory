"""Permissive UV bake adapter, derived from andrakis' MIT rasterizer.

See third_party/trellis288/NOTICE.md. Rows increase with UV v; samples are texel
centres. This is NOT a renderer. Overlap winner is highest source triangle id.
Bounded ragged candidate scheduling replaces the unsafe shared bounding grid.
Budget bounds candidate count, NOT total bytes (outputs and mesh also occupy RAM).
"""
import math
import torch


@torch.no_grad()
def rasterize_uv(uvs, faces, size, candidate_budget=262144, eps=1e-6, *, stats=None):
    if type(size) is not int or not 1 <= size <= 8192:
        raise ValueError("texture size must be integer 1..8192")
    if type(candidate_budget) is not int or not 1 <= candidate_budget <= 24_000_000:
        raise ValueError("candidate budget must be integer 1..24000000")
    if not math.isfinite(eps) or not 0 <= eps <= 1e-4:
        raise ValueError("invalid edge tolerance")
    if uvs.ndim != 2 or uvs.shape[1] != 2 or not uvs.is_floating_point():
        raise ValueError("UVs must be floating (V,2)")
    if faces.ndim != 2 or faces.shape[1] != 3 or faces.dtype not in (torch.int32, torch.int64):
        raise ValueError("faces must be integer (F,3)")
    if uvs.device != faces.device:
        raise ValueError("UV and face devices must match")
    if not torch.isfinite(uvs).all() or ((uvs < 0) | (uvs > 1)).any():
        raise ValueError("UVs must be finite within [0,1]")
    if faces.numel() and (faces.min() < 0 or faces.max() >= len(uvs)):
        raise ValueError("face index outside vertex array")
    device = uvs.device
    uvs, faces = uvs.to(torch.float32), faces.to(torch.long)
    tri_out = torch.full((size, size), -1, dtype=torch.long, device=device)
    bary_out = torch.zeros((size, size, 3), dtype=torch.float32, device=device)
    if stats is not None:
        stats.update(candidate_budget=candidate_budget, peak_candidates=0, chunks=0, total_candidates=0)
    if not len(faces):
        return tri_out >= 0, tri_out, bary_out
    p = uvs[faces] * size - 0.5
    x, y = p[..., 0], p[..., 1]
    d = (x[:, 1]-x[:, 0])*(y[:, 2]-y[:, 0]) - (x[:, 2]-x[:, 0])*(y[:, 1]-y[:, 0])
    xmin, ymin = p.amin(1).ceil().clamp(0, size-1).long().unbind(-1)
    xmax, ymax = p.amax(1).floor().clamp(0, size-1).long().unbind(-1)
    bw, bh = (xmax-xmin+1).clamp(min=0), (ymax-ymin+1).clamp(min=0)
    ids = torch.nonzero((d.abs() > 1e-12) & (bw > 0) & (bh > 0)).flatten()
    if not ids.numel():
        return tri_out >= 0, tri_out, bary_out
    # Concatenate each triangle's own rectangle conceptually, not physically.
    # Split this linear stream, including individual oversized rectangles.
    ends = torch.cumsum((bw*bh)[ids], 0)
    starts = ends - (bw*bh)[ids]
    total = int(ends[-1])
    if stats is not None:
        stats['total_candidates'] = total
    for start in range(0, total, candidate_budget):
        q = torch.arange(start, min(start+candidate_budget, total), device=device)
        slot = torch.searchsorted(ends, q, right=True)
        face_ids = ids[slot]
        local = q-starts[slot]
        cx = xmin[face_ids] + local % bw[face_ids]
        cy = ymin[face_ids] + local // bw[face_ids]
        px, py = cx.to(torch.float32), cy.to(torch.float32)
        x0, x1, x2 = (x[face_ids, k] for k in range(3))
        y0, y1, y2 = (y[face_ids, k] for k in range(3))
        dd = d[face_ids]
        w0 = ((x1-px)*(y2-py)-(x2-px)*(y1-py))/dd
        w1 = ((x2-px)*(y0-py)-(x0-px)*(y2-py))/dd
        w2 = 1-w0-w1
        inside = (w0 >= -eps) & (w1 >= -eps) & (w2 >= -eps)
        flat = (cy*size+cx)[inside]
        fs = face_ids[inside]
        weights = torch.stack([w0, w1, w2], -1)[inside]
        # Select once for both id and weights; avoid racing duplicate CUDA writes.
        order = torch.argsort(flat, stable=True)
        ordered = flat[order]
        last = torch.ones_like(ordered, dtype=torch.bool)
        last[:-1] = ordered[1:] != ordered[:-1]
        keep = order[last]
        tri_out.view(-1)[flat[keep]] = fs[keep]
        bary_out.view(-1, 3)[flat[keep]] = weights[keep]
        if stats is not None:
            stats['chunks'] += 1
            stats['peak_candidates'] = max(stats['peak_candidates'], len(q))
    return tri_out >= 0, tri_out, bary_out
