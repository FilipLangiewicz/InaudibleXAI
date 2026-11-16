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
| 2026-11-16 | ast-esc50-v3abcd | `2026-11-16_03_ast-esc50-v3abcd` | [inaudiblexai-ast-esc50-v3abcd](https://www.kaggle.com/code/rozaliachojnacka/inaudiblexai-ast-esc50-v3abcd) | T2 (issues #9, #10, #11): AST on the 100 ESC-50 clips of T1. Four variants on the CPU: v3a mpeg1 96 dB, v3b mpeg1 92 dB, v3c lin_abdulla 96 dB, v3d lin_abdulla 92 dB. Each variant also measures ViSQOL. Deletion vs between clips (JS): v3a 15.5 % [11.9, 19.4] outside (the same as v2), v3b 16.0 % [12.3, 19.9] outside, v3c 1.3 % [0.6, 2.2] within, v3d 1.6 % [0.9, 2.6] within. Top-1 vs between clips: mpeg1 34 %, lin_abdulla 12 % [5, 19], both outside. ViSQOL of the deletion: v3a 3.26, v3b 3.20, v3c 3.69, v3d 3.58 (resynthesis 4.73). 80 min on 4 CPU cores. AST inference took 58 min, thus a GPU is better for the next job. | complete |
