# Experimental environment

This file describes the setup that runs the experiments of the project. The rules for the team are in `AGENTS.md` and `KAGGLE.md`.

## Overview

| Part | Tool | Files |
|---|---|---|
| Virtual environment and lock | Poetry, Python 3.12 locally | `pyproject.toml`, `poetry.lock`, `poetry.toml` |
| Package | `inaudible`, layout with `src/`, Semantic Versioning (0.1.0) | `src/inaudible/` |
| Commands | just | `justfile` |
| Format, lint, types | ruff (line length 120), mypy for the core modules | `pyproject.toml` |
| Checks before each commit | pre-commit (ruff format, ruff check, mypy) | `.pre-commit-config.yaml` |
| Tests | pytest | `tests/` |
| Configs of the experiments | one YAML file for each run, separate from the code | `jobs/runs/<folder>/<codename>.yaml` |
| Compute | Kaggle (T4 GPU), local CPU for short tests | `jobs/`, `KAGGLE.md` |
| Experiment tracking | MLflow, local SQLite store | `mlflow.db` (not in git) |
| Data | ESC-50, downloaded in the job. The original files are not changed. | `data/clips/esc50_t1.csv` |

## Dependency groups

| Group | Packages | Where |
|---|---|---|
| main | NumPy, SciPy, soundfile, PyYAML, pandas | local machines and Kaggle |
| `models` (optional) | PyTorch, Transformers | Kaggle only |
| `dev` | pytest, ruff, mypy, pre-commit, Kaggle CLI, MLflow, Jupyter kernel, matplotlib | local machines only |

Kaggle has its own PyTorch GPU build. Thus a job installs only the package and its main dependencies.

## Commands

| Command | Action |
|---|---|
| `just install` | Install the locked environment. |
| `just test` | Run the tests. |
| `just lint` | Check the format, the lint rules and the types. |
| `just push <folder>` | Send a job to Kaggle. |
| `just fetch <folder>` | Download the small outputs of a job and record the run in MLflow. |
| `just mlflow` | Open the MLflow interface. |
| `just sessions` | Copy the agent sessions into `sessions/`. |

## One run of an experiment

To run an experiment on Kaggle, do these steps:

1. Write the config `jobs/runs/<date>_<nn>_<codename>/<codename>.yaml`.
2. Commit and push the branch.
3. Run `just push <folder>`.
4. Run `just fetch <folder>` after the job is complete.

The job clones the branch, installs the package with `pip install -e` and runs `run_experiment`. Each run writes these files into its output folder:

- `config.yaml`: the full config of the run.
- `environment.json`: the commit hash, the device, the model and the versions of Python, NumPy, SciPy, PyTorch and Transformers.
- `metrics.json`: the main results and the time of each step.
- `summary.csv`: the mean of each measure with the 95 % bootstrap interval.
- `clips.csv`: the values for each clip.
- `listening/`: the audio files for the listening test.

`jobs/JOBS.md` lists all jobs, their links and their results.

## Tests

The tests use signals with a known result. Examples: a quiet tone near a loud tone is masked, and the resynthesis without a change gives back the input. `tests/test_pipeline.py` runs the complete pipeline on a few clips with a small model. On 2026-11-06, `just test` passed 18 tests and `just lint` found no problems.

## Open items

- tox for two Python versions (3.11 and 3.12) is not set up yet.
- The Kaggle runs use Python 3.13. The local machines use Python 3.12.
- The MkDocs documentation is not set up yet.
