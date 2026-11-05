"""The complete pipeline on a few synthetic clips with a small model. It needs no network and no GPU."""

import json

import numpy as np
import pandas as pd
import soundfile as sf

from inaudible import experiment


class BandEnergyModel:
    """A small fixed classifier: a random projection of the log energy in frequency bands."""

    name = "band-energy"
    sample_rate = 16000

    def __init__(self, n_classes: int = 8) -> None:
        self.weights = np.random.default_rng(0).standard_normal((32, n_classes))
        self.labels = [f"class_{i}" for i in range(n_classes)]

    def logits(self, waveforms: list[np.ndarray]) -> np.ndarray:
        feats = []
        for w in waveforms:
            spec = np.abs(np.fft.rfft(w)) ** 2
            feats.append(np.log10(np.array([b.sum() for b in np.array_split(spec, 32)]) + 1e-12))
        return np.array(feats) @ self.weights


def test_pipeline_writes_all_results(tmp_path, monkeypatch):
    sr = 44100
    rng = np.random.default_rng(0)
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir()
    names = []
    for i in range(4):
        t = np.arange(sr) / sr
        x = 0.3 * np.sin(2 * np.pi * (300 + 200 * i) * t) + 0.01 * rng.standard_normal(sr)
        names.append(f"clip{i}.wav")
        sf.write(audio_dir / names[-1], x, sr)
    clip_list = tmp_path / "clips.csv"
    pd.DataFrame({"filename": names, "category": "test", "listen": [1, 0, 0, 0]}).to_csv(clip_list, index=False)
    monkeypatch.setattr(experiment, "PROJECT_DIR", tmp_path)
    cfg = {
        "codename": "smoke",
        "seed": 0,
        "data": {"clip_list": "clips.csv"},
        "masking": {"model": "mpeg1", "n_fft": 512, "playback_db": 96.0},
        "model": {"name": "band-energy"},
        "metrics": {"n_boot": 200},
    }
    out = tmp_path / "out"
    metrics = experiment.run_experiment(cfg, out, audio_dir, device="cpu", model=BandEnergyModel())

    for name in ["clips.csv", "summary.csv", "metrics.json", "config.yaml", "environment.json", "logits.npz"]:
        assert (out / name).exists()
    assert len(list((out / "listening").glob("clip0_*.wav"))) == 4
    assert metrics["n_clips"] == 4
    assert metrics["resynthesis.js_divergence"] < 1e-6
    assert json.loads((out / "metrics.json").read_text()) == metrics
