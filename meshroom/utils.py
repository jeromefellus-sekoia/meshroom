import os
from pathlib import Path
import shutil
from subprocess import check_call
import tomllib
import importlib.util
from typing import Iterable
from pydantic import BaseModel
from tabulate import tabulate as _tabulate

ROOT_DIR = Path(os.path.dirname(__file__))
UI_DIR = ROOT_DIR / ".." / "dist"


def read_file(directory: str, filename: str) -> str:
    """Read a file's content or return empty string if not exists"""
    try:
        with open(os.path.join(directory, filename)) as f:
            return f.read()
    except Exception:
        return ""


def read_toml(directory: Path, filename: str) -> dict:
    """Read a TOML file's content or return empty dict"""
    try:
        with open(directory / filename) as f:
            return tomllib.load(f)
    except Exception:
        return {}


VERSION = read_toml(ROOT_DIR / "..", "pyproject.toml").get("version", "0.0.0")


def tabulate(
    data,
    headers: Iterable[str] | None = None,
    formatters: dict | None = None,
):
    def _format(x):
        for t, f in (formatters or {}).items():
            if isinstance(x, t):
                return f(x)
        if x is None:
            return "-"
        if isinstance(x, (list, tuple, set)):
            if not x:
                return "-"
            return ", ".join(map(_format, x))
        if isinstance(x, BaseModel):
            return f"{x}"
        return x

    out = []
    for i in data:
        if isinstance(i, BaseModel):
            out.append([_format(getattr(i, h.lower().replace(" ", "_"), None)) for h in headers] if headers else i.model_dump())
        elif isinstance(i, dict):
            out.append([_format(i.get(h.lower().replace(" ", "_"))) for h in headers] if headers else i)
        else:
            out.append(i)
    return _tabulate(out, headers=headers or "keys", tablefmt="rounded_outline")


def git_pull(url: str, path: Path):
    if path.is_dir() and (path / ".git").is_dir():
        check_call(["git", "pull"], cwd=path)
    else:
        check_call(["git", "clone", url, path])


def import_module(path: Path | str):
    path = Path(path)
    if path.is_file():
        spec = importlib.util.spec_from_file_location(path.stem, path)
        pull = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pull)
        return pull
    return None


def list_functions_from_module(path: Path | str, startswith: str = ""):
    if module := import_module(path):
        return [getattr(module, func) for func in dir(module) if (not startswith or func.startswith("pull_")) and callable(getattr(module, func))]
    return []


def cp_rf(source_path: Path | str, dst_path: Path | str):
    """Force-copy the source_path to the dst_path, removing all existing files in the dst_path"""
    dst_path = Path(dst_path)
    dst_path.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(dst_path, ignore_errors=True)
    shutil.copytree(source_path, dst_path)
