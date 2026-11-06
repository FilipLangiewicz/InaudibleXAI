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
    job="$(echo "{{FOLDER}}" | cut -d_ -f3-)"
    bash jobs/kaggle.sh kernels output "rozaliachojnacka/inaudiblexai-$job" -p "jobs/runs/{{FOLDER}}/output" --file-pattern '(json|csv|yaml|wav|npz)$'
    for d in jobs/runs/{{FOLDER}}/output/*/; do poetry run python -c "from pathlib import Path; from inaudible.experiment import log_to_mlflow; print(log_to_mlflow(Path('$d')))"; done

# Copy the agent sessions of this project into sessions/ and remove secrets and e-mail addresses
sessions:
    #!/usr/bin/env bash
    set -euo pipefail
    poetry run python - <<'EOF'
    import json, re
    from pathlib import Path

    repo = Path.cwd().resolve()
    src = Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(repo))
    out = repo / "sessions"
    secrets = []
    if (repo / ".env").exists():
        for line in (repo / ".env").read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                value = line.split("=", 1)[1].strip().strip("\"'")
                if len(value) >= 8:
                    secrets.append(value)
    # The optional group keeps a JSON escape such as \n that comes before the address.
    email = re.compile(r"(\\[nrt])?[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

    def clean(text):
        for value in secrets:
            text = text.replace(value, "<redacted>")
        names = {m.group(0).split("@")[0].removeprefix(m.group(1) or "") for m in email.finditer(text)}
        text = email.sub(lambda m: (m.group(1) or "") + "<redacted>", text)
        # A local part without its domain can also show the address.
        for name in (n for n in names if len(n) >= 6):
            text = text.replace(name, "<redacted>")
        for line in filter(None, text.split("\n")):
            json.loads(line)
        return text

    for main in sorted(src.glob("*.jsonl")):
        first = json.loads(next(l for l in main.open(encoding="utf-8") if '"timestamp"' in l))
        date = first.get("timestamp") or re.search(r'"timestamp": ?"([0-9-]{10})', json.dumps(first)).group(1)
        name = f"{date[:10]}_{main.stem}"
        files = [(main, out / f"{name}.jsonl")]
        files += [(f, out / name / "subagents" / f.name) for f in sorted((src / main.stem / "subagents").glob("*.jsonl"))]
        for a, b in files:
            b.parent.mkdir(parents=True, exist_ok=True)
            b.write_text(clean(a.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
        print(name, len(files), "files")
    EOF

# Open the MLflow interface for the local runs
mlflow:
    poetry run mlflow ui --backend-store-uri sqlite:///mlflow.db
