# Commands of the project. Run "just" to show the list.
set shell := ["bash", "-cu"]

default:
    @just --list

# Install the environment (Poetry, .venv in the project folder)
install:
    poetry install

# Run the tests
test:
    poetry run pytest

# Check the format, the lint rules and the types
lint:
    poetry run ruff format --check src tests
    poetry run ruff check src tests
    poetry run mypy

# Run the Kaggle CLI with the account of the project, for example: just kaggle kernels list --mine
kaggle *ARGS:
    bash jobs/kaggle.sh {{ARGS}}

# Push a job folder to Kaggle, for example: just push 2026-11-05_01_ast-esc50-v1
push FOLDER:
    bash jobs/kaggle.sh kernels push -p jobs/runs/{{FOLDER}}

# Download the small outputs of a job and record the runs in the local MLflow store
fetch FOLDER:
    #!/usr/bin/env bash
    set -euo pipefail
    job="${FOLDER#*_*_}"
    bash jobs/kaggle.sh kernels output "rozaliachojnacka/inaudiblexai-$job" -p "jobs/runs/{{FOLDER}}/output" --file-pattern '(json|csv|yaml|wav|npz)$'
    for d in jobs/runs/{{FOLDER}}/output/*/; do poetry run python -c "from pathlib import Path; from inaudible.experiment import log_to_mlflow; print(log_to_mlflow(Path('$d')))"; done

# Open the MLflow interface for the local runs
mlflow:
    poetry run mlflow ui --backend-store-uri mlruns
