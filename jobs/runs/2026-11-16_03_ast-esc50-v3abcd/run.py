"""T2: AST on 100 ESC-50 clips with two masking models at two playback levels, and ViSQOL.

The job has one CPU process for each variant.
"""

import multiprocessing
import subprocess
import sys
from pathlib import Path

REPO = "https://github.com/FilipLangiewicz/InaudibleXAI.git"
BRANCH = "t2-masking-model-2"
CLONE = "/tmp/repo"  # Not in the output folder, so the clone is not an output.
CODENAMES = ["ast-esc50-v3a", "ast-esc50-v3b", "ast-esc50-v3c", "ast-esc50-v3d"]


def run(codename: str, worker: int) -> dict:
    import torch

    # The session has 4 cores and 4 processes, so each process uses one thread.
    torch.set_num_threads(1)
    sys.path.insert(0, f"{CLONE}/src")
    from inaudible.experiment import load_config, run_experiment

    out = Path(f"/kaggle/working/{codename}")
    metrics = run_experiment(load_config(codename), out, Path(f"/kaggle/temp/esc50-{worker}"), "cpu")
    print(codename, metrics, flush=True)
    return metrics


# A new process imports this file again, so the clone and the start must be only in the main process.
if __name__ == "__main__":
    subprocess.run(["git", "clone", "--depth", "1", "--branch", BRANCH, REPO, CLONE], check=True)
    out = subprocess.run(["git", "-C", CLONE, "rev-parse", "HEAD"], capture_output=True, text=True)
    print("commit", out.stdout.strip())
    # Editable install: the package finds the clip lists and the configs in the clone.
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-e", CLONE], check=True)
    with multiprocessing.get_context("spawn").Pool(len(CODENAMES)) as pool:
        pool.starmap(run, [(codename, i) for i, codename in enumerate(CODENAMES)])
