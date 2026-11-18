"""The complete pipeline on a few synthetic clips with a small model. It needs no network and no GPU."""

import json

import numpy as np
import pandas as pd
import pytest
import soundfile as sf
import yaml

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


def base_config() -> dict:
    return {
        "codename": "smoke",
        "seed": 0,
        "data": {"clip_list": "clips.csv"},
        "masking": {"n_fft": 512},
        "audibility": {"visqol": False},
        "model": {"name": "band-energy"},
        "metrics": {"n_boot": 200, "within_margin": 0.05},
    }


@pytest.fixture
def audio_dir(tmp_path, monkeypatch):
    """Four synthetic clips and their clip list in a temporary project folder."""
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
    return audio_dir


# ViSQOL is slow, so only one masking model runs it.
@pytest.mark.parametrize(("masking", "visqol"), [("mpeg1", False), ("lin_abdulla", True)])
def test_pipeline_writes_all_results(tmp_path, audio_dir, masking, visqol):
    cfg = base_config()
    cfg["masking"].update({"model": masking, "playback_db": 96.0})
    cfg["audibility"]["visqol"] = visqol
    out = tmp_path / "out"
    metrics = experiment.run_experiment(cfg, out, audio_dir, device="cpu", model=BandEnergyModel())

    for name in ["clips.csv", "summary.csv", "metrics.json", "config.yaml", "environment.json", "logits.npz"]:
        assert (out / name).exists()
    assert len(list((out / "listening").glob("clip0_*.wav"))) == 4
    assert metrics["n_clips"] == 4
    assert metrics["resynthesis.js_divergence"] < 1e-6
    summary = pd.read_csv(out / "summary.csv").set_index(["condition", "measure"])
    assert summary.loc[("resynthesis_vs_between", "js_divergence"), "verdict"] == "within"
    assert json.loads((out / "metrics.json").read_text()) == metrics
    assert (("audio", "visqol_deletion") in summary.index) == visqol
    if visqol:
        assert summary.loc[("audio", "visqol_resynthesis"), "mean"] > 4.5


GRID = {"masking.model": ["mpeg1", "lin_abdulla"], "masking.playback_db": [96.0, 92.0]}


def test_expand_grid_makes_all_variants():
    variants = experiment.expand_grid(base_config(), GRID)
    assert [v["codename"] for v in variants] == [
        "smoke-mpeg1-96",
        "smoke-mpeg1-92",
        "smoke-lin_abdulla-96",
        "smoke-lin_abdulla-92",
    ]
    assert variants[3]["masking"] == {"n_fft": 512, "model": "lin_abdulla", "playback_db": 92.0}
    assert variants[3]["variant"] == {"masking.model": "lin_abdulla", "masking.playback_db": 92.0}
    assert all(v["job"] == "smoke" for v in variants)
    # Each variant differs from the job config only in the grid keys.
    for v in variants:
        rest = {k: val for k, val in v.items() if k not in ("codename", "job", "variant")}
        del rest["masking"]["model"], rest["masking"]["playback_db"]
        assert rest == {k: val for k, val in base_config().items() if k != "codename"}


def test_expand_grid_rejects_a_value_in_two_places():
    cfg = base_config()
    cfg["masking"]["playback_db"] = 96.0
    with pytest.raises(ValueError, match="masking.playback_db"):
        experiment.expand_grid(cfg, GRID)


def test_shared_grid_is_the_grid_of_t3():
    grid = yaml.safe_load((experiment.PROJECT_DIR / "jobs" / "grid.yaml").read_text())
    assert grid == GRID


def test_load_variants(tmp_path, monkeypatch):
    job = tmp_path / "runs" / "2026-11-19_01_smoke"
    job.mkdir(parents=True)
    cfg = base_config()
    del cfg["codename"]
    (job / "smoke.yaml").write_text(yaml.safe_dump({**cfg, "grid": "jobs/grid.yaml"}))
    (job / "single.yaml").write_text(yaml.safe_dump(cfg))
    monkeypatch.setattr(experiment, "RUNS_DIR", tmp_path / "runs")
    assert len(experiment.load_variants("smoke")) == 4
    assert all("grid" not in v for v in experiment.load_variants("smoke"))
    assert experiment.load_variants("single") == [{**cfg, "codename": "single"}]


def test_mlflow_records_each_variant(tmp_path, audio_dir):
    import mlflow

    uri = f"sqlite:///{(tmp_path / 'mlflow.db').as_posix()}"
    for cfg in experiment.expand_grid(base_config(), GRID):
        out = tmp_path / "output" / cfg["codename"]
        experiment.run_experiment(cfg, out, audio_dir, device="cpu", model=BandEnergyModel())
        assert yaml.safe_load((out / "config.yaml").read_text())["variant"] == cfg["variant"]
        experiment.log_to_mlflow(out, uri)
    mlflow.set_tracking_uri(uri)
    runs = mlflow.search_runs(experiment_names=["inaudible"])
    assert sorted(runs["tags.variant"]) == sorted(
        f"masking.model={m}, masking.playback_db={p}"
        for m in GRID["masking.model"]
        for p in GRID["masking.playback_db"]
    )
    assert set(runs["tags.job"]) == {"smoke"}
    assert set(runs["params.masking.playback_db"]) == {"96.0", "92.0"}
