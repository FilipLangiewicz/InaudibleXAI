# Refuting result

We wrote this result down on 2026-11-05, before the first run at scale.

## The statement of the project card

The decision change and the attribution mass below the threshold stay within the between-clip control for every model and task. This applies at both playback levels and under both masking models.

## The test for one model and one task

We use these conditions (see `src/inaudible/experiment.py`):

- `deletion`: the sub-threshold deletion.
- `resynthesis`: STFT and inverse STFT without a change.
- `random_deletion`: the same number of bins per frame, removed at random lines.
- `between_clips`: the output of a different clip.

The main measure is the Jensen-Shannon divergence between the outputs. The other measures are the change of the top-1 class and the cosine distance of the logits. Each value has a 95 % bootstrap interval over the clips.

The deletion has no measurable effect on a model if both conditions are true:

1. The interval of `deletion` overlaps the interval of `resynthesis`.
2. The upper limit of the interval of `deletion` is less than 5 % of the mean of `between_clips`.

The project is refuted if this result occurs for every model and task, at both playback levels, under both masking models, and for the attribution mass.

The 5 % limit is a decision of the team. We can change it only before the run of all models (T3).
