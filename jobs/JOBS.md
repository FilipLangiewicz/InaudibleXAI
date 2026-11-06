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
| 2026-11-05 | ast-esc50-v1 | `2026-11-05_01_ast-esc50-v1` | [inaudiblexai-ast-esc50-v1](https://www.kaggle.com/code/rozaliachojnacka/inaudiblexai-ast-esc50-v1) | T1 prototype: AST on 100 ESC-50 clips, MPEG model 1 at 96 dB SPL. Deletion: top-1 change 0.33 [0.24, 0.42], JS 0.139 [0.107, 0.174]. Between clips: JS 0.893. Resynthesis: 0. 84 % of bins and 16 % of energy deleted, NMR -9.4 dB. 6 min on T4. | complete |
| 2026-11-06 | ast-esc50-v2 | `2026-11-06_02_ast-esc50-v2` | [inaudiblexai-ast-esc50-v2](https://www.kaggle.com/code/rozaliachojnacka/inaudiblexai-ast-esc50-v2) | T1 prototype, second run: the setup of ast-esc50-v1, plus the confidence drop, the band audibility check and the verdict (margin 5 %). Deletion vs between clips (JS): 15.5 % [11.9, 19.4], verdict outside. Confidence drop 0.117 [0.074, 0.162]. Band check: 44 % of cells audible (per bin: 0.5 %). 5 min on T4. | complete |
