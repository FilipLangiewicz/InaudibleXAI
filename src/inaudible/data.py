"""Clip lists and the download of ESC-50 clips."""

import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf

# A fixed commit of the ESC-50 repository keeps the clips the same in every run.
ESC50_COMMIT = "33c8ce9eb2cf0b1c2f8bcf322eb349b6be34dbb6"
ESC50_URL = f"https://raw.githubusercontent.com/karolpiczak/ESC-50/{ESC50_COMMIT}"


def make_esc50_list(meta_csv: str | Path, per_class: int, listen_classes: list[str], seed: int) -> pd.DataFrame:
    """Select per_class clips of each class. Mark the first clip of each listen class for the listening test."""
    meta = pd.read_csv(meta_csv)
    rng = np.random.default_rng(seed)
    rows = []
    for _, group in meta.groupby("target", sort=True):
        rows.append(group.iloc[np.sort(rng.choice(len(group), size=per_class, replace=False))])
    clips = pd.concat(rows, ignore_index=True)[["filename", "fold", "target", "category"]]
    first = ~clips.duplicated("category")
    clips["listen"] = (first & clips["category"].isin(listen_classes)).astype(int)
    return clips


def download_esc50(filenames: list[str], dest: Path) -> list[Path]:
    """Download the clips into dest. A clip that exists already is not downloaded again."""
    dest.mkdir(parents=True, exist_ok=True)
    paths = []
    for name in filenames:
        path = dest / name
        if not path.exists():
            urllib.request.urlretrieve(f"{ESC50_URL}/audio/{name}", path)
        paths.append(path)
    return paths


def read_audio(path: Path) -> tuple[np.ndarray, int]:
    """Read a clip as mono float64 with full scale 1.0."""
    x, sr = sf.read(path, dtype="float64", always_2d=True)
    return x.mean(axis=1), int(sr)
