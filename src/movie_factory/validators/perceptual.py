"""Decoded display-referred RGB reference comparison and stable-ID visibility.

The expected directory must be an independently rendered canonical revision (or
the same unchanged native file for no-op calibration). It must not be the initial
beauty image for a requested edit. Metrics never substitute for native checks.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from skimage.metrics import structural_similarity

GREEN = {"ssim_min": 0.98, "mae_max": 0.01}
YELLOW = {"ssim_min": 0.95, "mae_max": 0.03}


def _read(directory: Path, kind: str, shot: str) -> np.ndarray:
    with Image.open(directory / kind / f"{shot}.png") as image:
        if image.format != "PNG":
            raise ValueError(f"{kind}/{shot} is not PNG")
        image.load()
        return np.asarray(image.convert("RGB"), dtype=np.uint8)


def _legend(directory: Path) -> dict:
    with (directory / "mask-legend.json").open() as stream:
        legend = json.load(stream)
    if legend.get("encoding") != "rgb8" or not isinstance(legend.get("entities"), dict):
        raise ValueError("Missing supported stable-ID rgb8 mask legend")
    colors = legend["entities"]
    if len({tuple(color) for color in colors.values()}) != len(colors):
        raise ValueError("Mask legend has ambiguous duplicate colors")
    return colors


def _entity_mask(mask: np.ndarray, colors: dict, entity_id: str) -> np.ndarray:
    if entity_id not in colors:
        raise ValueError(f"Mask legend missing {entity_id}")
    color = np.asarray(colors[entity_id], dtype=np.int16)
    # Ignore antialiased boundaries beyond this small RGB distance. Interior
    # opaque ID pixels are exact; dark/shadow beauty pixels are never masks.
    return np.max(np.abs(mask.astype(np.int16)-color), axis=2) <= 12


def _expand(mask: np.ndarray, pixels: int) -> np.ndarray:
    image = Image.fromarray(mask.astype(np.uint8) * 255)
    return np.asarray(image.filter(ImageFilter.MaxFilter(2*pixels+1))) > 0


def _region_metrics(actual: np.ndarray, expected: np.ndarray, selection: np.ndarray, ssim_map: np.ndarray) -> dict:
    count = int(selection.sum())
    if count < 49:
        return {"applicable": False, "reason": "Fewer than 49 visible comparison pixels", "pixels": count, "ssim": None, "mae": None, "color": "YELLOW"}
    rows, columns = np.where(selection)
    mae = float(np.abs(actual-expected)[selection].mean())
    ssim = float(ssim_map[selection].mean())
    color = "GREEN" if ssim >= GREEN["ssim_min"] and mae <= GREEN["mae_max"] else "YELLOW" if ssim >= YELLOW["ssim_min"] and mae <= YELLOW["mae_max"] else "RED"
    return {"applicable": True, "pixels": count, "crop_xyxy": [int(columns.min()), int(rows.min()), int(columns.max()+1), int(rows.max()+1)], "ssim": ssim, "mae": mae, "color": color}


def compare_renders(actual_dir: str | Path, expected_dir: str | Path, baseline_dir: str | Path | None = None) -> dict:
    actual_dir, expected_dir = Path(actual_dir), Path(expected_dir)
    baseline_dir = Path(baseline_dir) if baseline_dir else None
    result = {"passed": False, "color": "RED", "shots": {}, "errors": [], "policy": {
        "version": "3d01-perceptual-v1", "green": GREEN, "yellow": YELLOW,
        "decode": "PNG display-referred RGB in [0,1]; no additional gamma conversion",
        "ssim": "scikit-image channel_axis=-1, data_range=1, win_size=7; local SSIM map averaged over each selected region",
        "regions": "union of baseline, actual and expected stable-ID masks, expanded by ceil(8*width/1280) pixels; remaining region is complement",
        "visibility": "opaque visible mask pixels / full image pixels; helmet A/B >=0.002, C >=0.05; table A/B >=0.01"}}
    try:
        actual_shots = {p.stem for p in (actual_dir / "renders").glob("shot_*.png")}
        expected_shots = {p.stem for p in (expected_dir / "renders").glob("shot_*.png")}
        if not actual_shots or actual_shots != expected_shots or not actual_shots <= {"shot_A", "shot_B", "shot_C"}:
            raise ValueError(f"Render shot inventories differ or are empty: actual={sorted(actual_shots)}, expected={sorted(expected_shots)}")
        directories = {"actual": actual_dir, "expected": expected_dir}
        if baseline_dir:
            directories["baseline"] = baseline_dir
        legends = {label: _legend(directory) for label, directory in directories.items()}
        if any(legend != legends["actual"] for legend in legends.values()):
            raise ValueError("Stable-ID mask legend changed between scene stages")
        colors = []
        for shot in sorted(expected_shots):
            frames = {label: _read(directory, "renders", shot) for label, directory in directories.items()}
            masks = {label: _read(directory, "masks", shot) for label, directory in directories.items()}
            shape = frames["expected"].shape
            if min(shape[:2]) < 7 or any(frame.shape != shape for frame in [*frames.values(), *masks.values()]):
                raise ValueError(f"{shot}: mismatched or unsupported image dimensions")
            for label, frame in frames.items():
                if float(frame.astype(np.float64).std()) < 1.0:
                    raise ValueError(f"{shot}/{label}: blank or effectively constant render")
            actual = frames["actual"].astype(np.float64)/255.0
            expected = frames["expected"].astype(np.float64)/255.0
            score, local_map = structural_similarity(actual, expected, data_range=1.0, channel_axis=-1, win_size=7, full=True)
            local_map = local_map.mean(axis=2)
            regions = {}
            visibility = {}
            union = np.zeros(shape[:2], dtype=bool)
            for entity_id, label in (("helmet_01", "helmet"), ("coffee_table_01", "table")):
                entity_masks = {stage: _entity_mask(mask, legends[stage], entity_id) for stage, mask in masks.items()}
                threshold = (0.05 if shot == "shot_C" else 0.002) if label == "helmet" else (0 if shot == "shot_C" else 0.01)
                visibility[label] = {}
                for stage, entity_mask in entity_masks.items():
                    fraction = float(entity_mask.mean())
                    passed = fraction >= threshold
                    visibility[label][stage] = {"fraction": fraction, "minimum": threshold, "passed": passed}
                    if not passed:
                        result["errors"].append(f"{shot}/{stage}/{label}: visibility {fraction:.6f} below {threshold:.6f}")
                region = _expand(np.logical_or.reduce(list(entity_masks.values())), max(1, math.ceil(8*shape[1]/1280)))
                union |= region
                regions[label] = _region_metrics(actual, expected, region, local_map)
                regions[label]["required"] = bool(threshold)
                if regions[label]["applicable"]:
                    colors.append(regions[label]["color"])
                elif threshold:
                    colors.append("RED")
                    result["errors"].append(f"{shot}/{label}: required region has insufficient visible pixels")
            regions["remaining"] = _region_metrics(actual, expected, ~union, local_map)
            regions["full_frame"] = _region_metrics(actual, expected, np.ones(shape[:2], dtype=bool), local_map)
            # Standard SSIM's full-frame average excludes the filter border. Keep
            # its reported scalar for reproducibility as well as region-map SSIM.
            regions["full_frame"]["standard_ssim"] = float(score)
            colors.extend(regions[key]["color"] for key in ("full_frame", "remaining"))
            result["shots"][shot] = {"width": shape[1], "height": shape[0], "regions": regions, "visibility": visibility}
        rank = {"GREEN": 0, "YELLOW": 1, "RED": 2}
        result["color"] = "RED" if result["errors"] else max(colors, key=rank.get)
        result["passed"] = result["color"] == "GREEN"
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        result["errors"].append(f"Render validation failed: {type(exc).__name__}: {exc}")
    return result


def validate_visibility(directory: str | Path) -> dict:
    """Validate baseline image/mask inventory and visibility without an edit oracle."""
    result = compare_renders(directory, directory)
    result["purpose"] = "Image/mask validity and visibility only; self-comparison is not revision evidence"
    return result
