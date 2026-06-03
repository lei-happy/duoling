"""
路线折线 JSON 编解码与抽稀（地图预览用）
"""

from __future__ import annotations

import json
from typing import Any, List, Optional

MAX_STORED_POLYLINE_POINTS = 800


def simplify_polyline_path(
    path: List[List[float]],
    *,
    max_points: int = MAX_STORED_POLYLINE_POINTS,
) -> List[List[float]]:
    if len(path) <= max_points:
        return path
    if max_points < 2:
        return path[:1] if path else []
    n = len(path)
    indices = {0, n - 1}
    step = (n - 1) / (max_points - 1)
    for i in range(1, max_points - 1):
        indices.add(int(round(i * step)))
    ordered = sorted(indices)
    return [path[i] for i in ordered]


def encode_route_polyline(path: Optional[List[List[float]]]) -> Optional[str]:
    if not path:
        return None
    cleaned: List[List[float]] = []
    for pt in path:
        if not isinstance(pt, (list, tuple)) or len(pt) < 2:
            continue
        try:
            lng, lat = float(pt[0]), float(pt[1])
        except (TypeError, ValueError):
            continue
        if cleaned and cleaned[-1][0] == lng and cleaned[-1][1] == lat:
            continue
        cleaned.append([lng, lat])
    if len(cleaned) < 2:
        return None
    stored = simplify_polyline_path(cleaned)
    return json.dumps(stored, separators=(",", ":"))


def decode_route_polyline(raw: Optional[str]) -> List[List[float]]:
    if not raw or not str(raw).strip():
        return []
    try:
        data: Any = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if isinstance(data, dict):
        data = data.get("path") or data.get("polylinePath") or []
    if not isinstance(data, list):
        return []
    out: List[List[float]] = []
    for pt in data:
        if not isinstance(pt, (list, tuple)) or len(pt) < 2:
            continue
        try:
            out.append([float(pt[0]), float(pt[1])])
        except (TypeError, ValueError):
            continue
    return out
