"""One experiment: sub-threshold deletion on a clip list, and the change of the model output.

Conditions, each compared with the output for the original clip:
- resynthesis: STFT and inverse STFT without a change (the effect of the resynthesis alone)
- deletion: all bins below the masking threshold removed
- random_deletion: the same number of bins per frame removed at random lines (a change of the same size)
- between_clips: the original output of a different clip (the between-clip control)
"""

import json
import platform
import subprocess
import time
from math import gcd
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf
import yaml
from scipy.signal import resample_poly

from inaudible.data import download_esc50, read_audio
from inaudible.deletion import delete_random, delete_subthreshold, noise_to_mask, resynthesize
from inaudible.masking import Model1
from inaudible.metrics import between_clip_pairs, bootstrap_ci, output_change
from inaudible.models import AudioClassifier, build_model

PROJECT_DIR = Path(__file__).resolve().parents[2]
RUNS_DIR = PROJECT_DIR / "jobs" / "runs"
CONDITIONS = ["resynthesis", "deletion", "random_deletion"]


def load_config(codename: str) -> dict:
    matches = sorted(RUNS_DIR.glob(f"*/{codename}.yaml"))
    if len(matches) != 1:
        raise FileNotFoundError(f"need exactly one config for {codename}, found {matches}")
    cfg = yaml.safe_load(matches[0].read_text())
    cfg["codename"] = codename
    return cfg


def _commit() -> str:
    out = subprocess.run(["git", "-C", str(PROJECT_DIR), "rev-parse", "HEAD"], capture_output=True, text=True)
    return out.stdout.strip() or "unknown"


def _versions() -> dict[str, str]:
    versions = {"python": platform.python_version()}
    for name in ["numpy", "scipy", "torch", "transformers"]:
        try:
            versions[name] = __import__(name).__version__
        except ImportError:
            pass
    return versions


def _resample(x: np.ndarray, sr: int, target: int) -> np.ndarray:
    if sr == target:
        return x
    g = gcd(sr, target)
    return np.asarray(resample_poly(x, target // g, sr // g))


def process_clips(cfg: dict, paths: list[Path], listen: list[bool], out_dir: Path, target_sr: int):
    """Apply all conditions to each clip. Returns the waveforms at target_sr and a table of audio statistics."""
    mcfg = cfg["masking"]
    rng = np.random.default_rng(cfg["seed"])
    waves: dict[str, list[np.ndarray]] = {c: [] for c in ["original", *CONDITIONS]}
    rows = []
    for path, is_listen in zip(paths, listen, strict=True):
        x, sr = read_audio(path)
        model = Model1(sr, mcfg["n_fft"], mcfg["playback_db"])
        res = delete_subthreshold(x, model)
        versions = {
            "original": x,
            "resynthesis": resynthesize(x, mcfg["n_fft"]),
            "deletion": res.deleted,
            "random_deletion": delete_random(x, res.audible, mcfg["n_fft"], rng),
        }
        row = {
            "filename": path.name,
            "fraction_bins_deleted": res.fraction_bins_deleted,
            "fraction_energy_deleted": res.fraction_energy_deleted,
        }
        for c in CONDITIONS:
            for key, value in noise_to_mask(x, versions[c], res.threshold_db, model).items():
                row[f"{key}_{c}"] = value
        rows.append(row)
        for c, w in versions.items():
            waves[c].append(_resample(w, sr, target_sr))
        if is_listen:
            ldir = out_dir / "listening"
            ldir.mkdir(parents=True, exist_ok=True)
            stem = path.stem
            for name, w in [
                ("original", x),
                ("deleted", res.deleted),
                ("residual", x - res.deleted),
                ("random", versions["random_deletion"]),
            ]:
                sf.write(ldir / f"{stem}_{name}.wav", w, sr, subtype="FLOAT")
    return waves, pd.DataFrame(rows)


def run_experiment(
    cfg: dict,
    out_dir: Path,
    audio_dir: Path,
    device: str = "cuda",
    model: AudioClassifier | None = None,
) -> dict:
    """Run the full pipeline and write the results into out_dir. Returns the summary metrics."""
    out_dir.mkdir(parents=True, exist_ok=True)
    clips = pd.read_csv(PROJECT_DIR / cfg["data"]["clip_list"])
    if cfg["data"].get("n_clips"):
        clips = clips.iloc[: cfg["data"]["n_clips"]].reset_index(drop=True)
    paths = download_esc50(clips["filename"].tolist(), audio_dir)

    t0 = time.time()
    if model is None:
        model = build_model(cfg["model"], device)
    t_model_load = time.time() - t0

    t0 = time.time()
    waves, audio_stats = process_clips(cfg, paths, clips["listen"].astype(bool).tolist(), out_dir, model.sample_rate)
    t_deletion = time.time() - t0

    t0 = time.time()
    logits = {c: model.logits(w) for c, w in waves.items()}
    t_inference = time.time() - t0

    rng = np.random.default_rng(cfg["seed"] + 1)
    partner = between_clip_pairs(len(clips), rng)
    changes = {c: output_change(logits["original"], logits[c]) for c in CONDITIONS}
    changes["between_clips"] = output_change(logits["original"], logits["original"][partner])

    table = clips.merge(audio_stats, on="filename")
    table["top1_original"] = [model.labels[i] for i in logits["original"].argmax(1)]
    table["top1_deletion"] = [model.labels[i] for i in logits["deletion"].argmax(1)]
    for c, measures in changes.items():
        for m, values in measures.items():
            table[f"{m}_{c}"] = values
    table.to_csv(out_dir / "clips.csv", index=False)

    rows = []
    for c, measures in changes.items():
        for m, values in measures.items():
            mean, lo, hi = bootstrap_ci(values, rng, cfg["metrics"]["n_boot"])
            rows.append({"condition": c, "measure": m, "mean": mean, "ci_low": lo, "ci_high": hi})
    for col in audio_stats.columns.drop("filename"):
        mean, lo, hi = bootstrap_ci(audio_stats[col].to_numpy(), rng, cfg["metrics"]["n_boot"])
        rows.append({"condition": "audio", "measure": col, "mean": mean, "ci_low": lo, "ci_high": hi})
    summary = pd.DataFrame(rows)
    summary.to_csv(out_dir / "summary.csv", index=False)

    metrics = {f"{r.condition}.{r.measure}": r.mean for r in summary.itertuples()}
    metrics.update(
        {
            "time.model_load_s": t_model_load,
            "time.deletion_s": t_deletion,
            "time.inference_s": t_inference,
            "n_clips": len(clips),
        }
    )
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    (out_dir / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    env = {"commit": _commit(), "device": device, "model": model.name, "versions": _versions()}
    (out_dir / "environment.json").write_text(json.dumps(env, indent=2))
    np.savez_compressed(out_dir / "logits.npz", partner=partner, **logits)
    return metrics


def log_to_mlflow(out_dir: Path, tracking_uri: str | None = None) -> str:
    """Record a downloaded run in the local MLflow store (default: mlruns/ in the project). Returns the run id."""
    import mlflow

    mlflow.set_tracking_uri(tracking_uri or (PROJECT_DIR / "mlruns").as_uri())
    cfg = yaml.safe_load((out_dir / "config.yaml").read_text())
    env = json.loads((out_dir / "environment.json").read_text())
    metrics = json.loads((out_dir / "metrics.json").read_text())
    mlflow.set_experiment(cfg.get("experiment", "inaudible"))
    with mlflow.start_run(run_name=cfg["codename"]) as run:
        flat = pd.json_normalize(cfg, sep=".").iloc[0].to_dict()
        mlflow.log_params({**flat, "commit": env["commit"], **{f"version.{k}": v for k, v in env["versions"].items()}})
        mlflow.log_metrics(metrics)
        for name in ["clips.csv", "summary.csv", "config.yaml", "environment.json"]:
            mlflow.log_artifact(str(out_dir / name))
        return str(run.info.run_id)
