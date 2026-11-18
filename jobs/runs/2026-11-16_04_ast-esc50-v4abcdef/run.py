"""T2: AST on 100 ESC-50 clips, a sweep of lower playback levels for the two masking models, with ViSQOL.

The deletion and ViSQOL use the CPU. Thus the job starts one process for each variant on the 4 cores.
AST runs on the two GPUs, because it took 58 min on the CPU in ast-esc50-v3abcd.
"""

import subprocess
import sys
from pathlib import Path

REPO = "https://github.com/FilipLangiewicz/InaudibleXAI.git"
BRANCH = "t2-masking-model-2"
CLONE = "/tmp/repo"  # Not in the output folder, so the clone is not an output.
CODENAMES = [f"ast-esc50-v4{letter}" for letter in "abcdef"]


def run(codename: str, worker: int) -> dict:
    import torch

    # More processes than cores: one thread for each process prevents oversubscription.
    torch.set_num_threads(1)
    device = f"cuda:{worker % 2}"
    torch.cuda.set_device(device)
    sys.path.insert(0, f"{CLONE}/src")
    from inaudible.experiment import load_config, run_experiment

    out = Path(f"/kaggle/working/{codename}")
    metrics = run_experiment(load_config(codename), out, Path(f"/kaggle/temp/esc50-{worker}"), device)
    print(codename, metrics, flush=True)
    return metrics


# A new process imports this file again, so the clone and the start must be only in the main process.
if __name__ == "__main__":
    import torch

    assert torch.cuda.device_count() == 2, "this job needs 2 GPUs (T4 x2)"
    subprocess.run(["git", "clone", "--depth", "1", "--branch", BRANCH, REPO, CLONE], check=True)
    out = subprocess.run(["git", "-C", CLONE, "rev-parse", "HEAD"], capture_output=True, text=True)
    print("commit", out.stdout.strip(), flush=True)
    # Editable install: the package finds the clip lists and the configs in the clone.
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-e", CLONE], check=True)
    with torch.multiprocessing.get_context("spawn").Pool(len(CODENAMES)) as pool:
        pool.starmap(run, [(codename, i) for i, codename in enumerate(CODENAMES)])
