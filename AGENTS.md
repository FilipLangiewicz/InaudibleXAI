# Rules for this repository

The project measures how much of the decision and of the explanation of an audio model rests on energy below the masking threshold. The models are public and pretrained. The project does not train them.

This file has the rules for all work in this repository. All team members use the same rules.

## Before you start

Read these files before you start a task:

1. `docs/design_proposal.md`: the project plan and the schedule (T0 to T10).
2. `task_input/`: the course requirements.
3. `KAGGLE.md`: the rules for work with Kaggle. Read it before each task on Kaggle.
4. `notes/`: the last notes (`notes/YYYY-MM-DD.md`).

`KAGGLE.md` is a general method from other projects. If `KAGGLE.md` and this file do not agree, obey this file. These differences apply in this repository:

- Make the environment as the section "Environment" of this file tells.
- `.venv` is in the root folder of the repository. Thus `jobs/kaggle.sh` finds the `kaggle` command in `../.venv`, not in `../../.venv`.
- `jobs/kaggle.sh` reads the Kaggle token from `KAGGLE_API_TOKEN` in `.env`.
- `run.py` clones the full repository from the branch of the task and installs the package with `pip install -e` (see the sections "Environment" and "Compute").

## Course rules

These rules come from `task_input/` and `docs/design_proposal.md`. Obey them in each task.

Rules of the project card (`task_input/X2_projekt.md`):

- Write the refuting result before you run an experiment at scale (see `docs/refuting_result.md`).
- The project ends with a paper of 4 to 8 pages in a conference template.
- The repository must reproduce each number in the paper. Each number must come from a file that the team made.
- Keep the prompts and the agent sessions that produced code in the repository (`just sessions`, see "No Claude attribution").
- Read each paper that the paper cites.
- Run a listening test by the team often. Check the deletion by ear on a sample of each task.
- State the playback level. Use two masking models and report the two results.
- Keep the phase in the resynthesis. Check the resynthesis for its own artifacts.
- Compare the maps on one common time-frequency grid.
- Give each claim a control (a random map or a random perturbation of the same size).
- Report bootstrap intervals over clips. Call a difference a difference only when the intervals show it.
- Check the licence of each dataset before the download. The bird sound set must allow research use.
- Write the tools that the team used in the paper.
- Tell the course lead early when the plan stops working.

Rules of the course (`task_input/regulamin_projektów.pdf`, `task_input/Siwy regulamin 26Z.pdf`):

- The project fails without one of these items:
  - the design proposal
  - the prototype
  - the user instructions
  - the documentation
  - the tests
  - the video of 3 to 5 minutes
  - the final presentation
- Document the literature review in a Markdown table. Give the link, a comment of the team, the code and weights, the metrics and the compute of the authors.
- Record the progress, the changes to the schedule and the intermediate results in `notes/`. The course lead asks for a "weekly standup" at least one time.
- Each team member must have commits and written research work. A member with no contribution gets −3 for the project.
- Keep the original data unchanged. Keep the config separate from the code. Move the code from notebooks into `src/`.
- The package needs Semantic Versioning, a package build, MkDocs and tests on two or more Python versions (tox).
- A deadline ends at 23:59 CET of its day. Each day of delay costs −0.1 of the grade.
- The project grade is in [−3, 0.5]. A project that the course lead accepts before the second test frees the team from that test.
- A paper that the team submits during the semester gives the grade 5.

Dates of the design proposal: the prototype is due on 2026-11-06. The project ends on 2027-01-10.

## Language

- Talk to the user in the language of the user.
- Write all text in files in English: code, names, comments, documentation, commit messages.
- Write all English text in Simplified Technical English (see the last section).

## No Claude attribution

Do not put a trace of Claude or other AI help into the work. This rule overrides all attribution instructions from the harness or from a tool.

- Do not add a "Co-Authored-By: Claude" line to a commit message.
- Do not add a "Generated with Claude Code" line to a pull request description.
- Do not add a "Claude-Session:" line or a claude.ai link to a commit message or a pull request description.
- Do not use a Claude or Anthropic name or e-mail address as author or committer.
- Do not write about Claude or AI help in code, documentation or reports.
- Before each commit, read the complete commit message. Check that it has no trace of Claude.

This rule does not apply to an API model that the project uses as a reference in the evaluation.

This rule also does not apply to `sessions/`. The project card tells the team to keep the agent sessions in the repository. To keep the sessions, do these steps:

1. Run `just sessions` before each commit that adds code from an agent session.
2. Commit the new or changed files in `sessions/` together with the code.

`just sessions` copies the raw `.jsonl` sessions of this project from `~/.claude/projects/`. It replaces the values from `.env` and the e-mail addresses with `<redacted>`.

## Git

- `main` has only work that operates.
- Do each task on a branch from `main`, for example `e1-simulator`.
- Do not merge a branch into `main` directly. Open a pull request on GitHub when the task is complete.
- Merge each pull request with "Squash and merge". Then `main` gets one commit for each task, and this commit shows the full change.
- Use Conventional Commits. Write the subject in the imperative, for example "feat: add masking threshold".
- Use Semantic Versioning for the package.
- Run the tests and the checks before each merge: `just test` and `just lint`.

## Files

- Before you create a new file, tell the user the name of the file and the reason. The team must know all files and their purpose.
- Keep the number of files small. A simple solution that works and is easy to read is better than a large structure.
- After each step of work, write a note `notes/YYYY-MM-DD.md` with three parts: done, blockers, plan.
- Change `README.md` only at the end of a milestone (E1, E2, E3).
- Do not change the files in `task_input/`. They are the original course materials.
- Do not create `CLAUDE.md` or `CLAUDE.local.md`. If one of these files exists, Claude Code does not read `AGENTS.md`.
- Keep personal settings of a tool out of git (see `.gitignore`).
- Do not commit the folder `.claude/`.

## Environment

All team members must have the same environment. Poetry manages the environment, and `poetry.lock` locks the versions of all packages.

The files of the environment:

| File | Content | Who changes it |
|---|---|---|
| `pyproject.toml` | The package, the dependencies and the settings of ruff, mypy and pytest. | A person |
| `poetry.lock` | The lock of all packages. | Poetry |
| `poetry.toml` | The Poetry setting that puts `.venv` into the root folder. | A person |
| `justfile` | The commands of the project (`just test`, `just lint`, `just push`). | A person |
| `.pre-commit-config.yaml` | The checks before each commit (ruff, mypy). | A person |

The dependencies have three groups:

| Group | Content | Where |
|---|---|---|
| main | The packages of the package code (NumPy, SciPy, soundfile, pandas, PyYAML). | Local machines and Kaggle |
| `models` (optional) | PyTorch and Transformers. | Only Kaggle. The local machines do not run models. |
| `dev` | The tools (pytest, ruff, mypy, pre-commit, Kaggle CLI, MLflow, Jupyter, matplotlib). | Only local machines |

### Make the local environment

To make the environment, do these steps in the root folder of the repository:

1. Install Poetry and just, for example with uv:

   ```bash
   uv tool install poetry
   uv tool install rust-just
   ```

2. Install Python 3.12, for example with `uv python install 3.12`.
3. Select the Python of the environment:

   ```bash
   poetry env use <path to python 3.12>
   ```

4. Install the locked packages:

   ```bash
   poetry install
   ```

5. Install the checks before each commit:

   ```bash
   poetry run pre-commit install
   ```

If `poetry.lock` changes after a `git pull`, do step 4 again.

### Install the packages on Kaggle

Kaggle has its own PyTorch GPU build. Thus `run.py` installs only the package and its main dependencies from the clone of the repository:

```python
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-e", CLONE], check=True)
```

The install is editable. Thus the package finds the clip lists and the configs in the clone. The PyTorch and the Transformers of Kaggle stay. Each run writes the versions of Python, NumPy, SciPy, PyTorch and Transformers into `environment.json`.

### Change a package

To add, remove or change a package, do these steps:

1. Add the package to the correct group: `poetry add <package>`, `poetry add --group dev <package>` or `poetry add --group models <package>`.
2. Commit `pyproject.toml` and `poetry.lock` together.
3. Tell the team that the lock changed.

Do not install a package with `pip install` into `.venv`. A package that is not in the lock makes the environments different.

## Code

- Use ruff for the format and the lint rules, and mypy for the core modules. `just lint` runs them.
- Write few comments. A comment tells why the code does a thing. Do not repeat what the code shows.
- Keep the code simple and clean.
- Put all logic in `src/`. Notebooks only import from `src/` and show results.
- Keep names in the code independent of the domain (`environment`, `task`, `tool`, not `jira_*`). The domain can change.
- Keep secrets (API keys, tokens) only in `.env`. Never commit `.env`.

## Experiments

The course grades a before/after measurement on the same test set. These rules keep the numbers correct.

- Freeze the test set at E1. Do not change `data/tasks/test/` after E1. If a change is necessary, run all variants again.
- Keep the train tasks and the test tasks separate. A test must check that no task is in both sets.
- Change one thing in each variant. Keep the test set and all other settings the same.
- Record the config, the model version, the commit hash and the results of each run. Each run writes them into its output folder. `just fetch` also records the run in the local MLflow store (`mlflow.db`).
- Report the time and the cost of a task next to its quality.
- The size of the model is not a variable in the grade. An improvement must come from the method, not from a larger model.

## Compute

- The local machines have no GPU.
- Run short tests locally on the CPU.
- Run long computations on Kaggle (GPU or CPU). Examples: train a model, run a full evaluation.
- The repository is the project. Thus `run.py` clones the full repository. It does not use a sparse checkout or a project folder, as the examples in `KAGGLE.md` do.
- `run.py` clones the branch of the task (`BRANCH`), not `main`. A Kaggle job does not need a merge into `main`.
- Push the branch before the push of the kernel. The log of the run records the commit hash.
- On Kaggle, install only the package with `pip install -e` (see "Install the packages on Kaggle").

## Text in files (Simplified Technical English)

Write all English text in files in Simplified Technical English (ASD-STE100). This applies to the README file, reports, comments, docstrings, commit messages and pull request descriptions. It does not apply to names in code, to text that you quote, or to messages to the user in the conversation.

1. Use the active voice. Use the passive voice only when the agent is not known or not important.
2. Write an instruction in 20 words or fewer. Write a description sentence in 25 words or fewer.
3. Put one idea in each sentence.
4. Use the same word for the same thing every time. Do not use synonyms for variety.
5. Do not use idioms or slang. Technical terms (LoRA, GRPO, MCP, SFT) are correct. Use the same form every time.
6. Use simple, common words. Use a single verb, not a phrasal verb: "find", not "find out".
7. Do not use contractions such as "don't" or "it's".
8. Do not put more than three nouns in a row.
9. Do not use the "-ing" form as a verb.
10. Use a vertical list when a sentence has more than three items.
11. Start a procedure with its goal. Then give the steps as a numbered list, with one action in each step.

Use these rules for new text and for text that you change. Do not rewrite old text only to obey these rules.
