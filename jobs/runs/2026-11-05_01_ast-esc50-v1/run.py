"""T1 prototype: sub-threshold deletion on 100 ESC-50 clips and the change of the AST output."""

import subprocess
import sys
from pathlib import Path

REPO = "https://github.com/FilipLangiewicz/InaudibleXAI.git"
BRANCH = "t1-prototype"
CLONE = "/tmp/repo"  # Not in the output folder, so the clone is not an output.
CODENAMES = ["ast-esc50-v1"]

import torch  # noqa: E402

assert torch.cuda.is_available(), "no GPU: check the phone verification of the account"
print("torch", torch.__version__, torch.cuda.get_device_name(0))

subprocess.run(["git", "clone", "--depth", "1", "--branch", BRANCH, REPO, CLONE], check=True)
print("commit", subprocess.run(["git", "-C", CLONE, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip())
# Editable install: the package finds the clip lists and the configs in the clone.
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-e", CLONE], check=True)
sys.path.insert(0, f"{CLONE}/src")

from inaudible.experiment import load_config, run_experiment  # noqa: E402

for codename in CODENAMES:
    metrics = run_experiment(load_config(codename), Path(f"/kaggle/working/{codename}"), Path("/kaggle/temp/esc50"))
    print(codename, metrics)
