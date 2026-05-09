"""
快照文件读写

统一处理：
  - JSON 格式：UTF-8 / indent=2 / ensure_ascii=False / 末尾换行
  - 文件名约定：与 exporters.EXPORTERS 中第二项一致
  - 元数据：snapshots/_meta.json 持有上次导出环境、git_sha、时间戳
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

META_FILENAME = "_meta.json"


def write_json(path: Path, data: Any) -> None:
    """格式化写盘，确保 git diff 友好（稳定排序由 exporter 自己保证）"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write("\n")


def read_json(path: Path) -> Any:
    if not path.is_file():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_meta(snapshot_dir: Path) -> Dict[str, Any]:
    return read_json(snapshot_dir / META_FILENAME) or {}


def write_meta(snapshot_dir: Path, meta: Dict[str, Any]) -> None:
    write_json(snapshot_dir / META_FILENAME, meta)


def get_git_sha(repo_root: Path) -> Optional[str]:
    """读取当前 HEAD commit，失败返回 None（CI/无 git 时不影响主流程）"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    return None


def get_git_branch(repo_root: Path) -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    return None


def make_meta(
    *,
    env: str,
    api_base: str,
    repo_root: Path,
    exported_by: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "env": env,
        "api_base": api_base,
        "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "git_sha": get_git_sha(repo_root),
        "git_branch": get_git_branch(repo_root),
        "exported_by": exported_by,
        "schema_version": 1,
    }
