# Jobs on Kaggle

The procedure for a job is in `KAGGLE.md` (sections 6 and 8). In short:

1. Commit and push the branch.
2. Add a row to this table with the status `to run`.
3. Push the kernel: `bash jobs/kaggle.sh kernels push -p jobs/runs/<folder>`.
4. Follow it in the background: `bash jobs/wait.sh rozaliachojnacka/inaudiblexai-<job> <job>`.
5. Download the small outputs into `jobs/runs/<folder>/output` and commit them.

Status values: to run, waiting for another job, queued, running, complete, failed, cancelled. The status cell has only one of these values, because `wait.sh` changes it. Put results into the comment.

| Date | Job | Folder | Link | Comment | Status |
|---|---|---|---|---|---|
| 2026-11-05 | ast-esc50-v1 | `2026-11-05_01_ast-esc50-v1` | [inaudiblexai-ast-esc50-v1](https://www.kaggle.com/code/rozaliachojnacka/inaudiblexai-ast-esc50-v1) | T1 prototype: AST on 100 ESC-50 clips, MPEG model 1 at 96 dB SPL. | to run |
