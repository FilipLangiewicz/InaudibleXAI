# Research hypotheses and the refuting result

We wrote these hypotheses on 2026-11-05, before the first run at scale. We can change the decision rules only before the run of all models (T3).

## The question

Do audio models use sound that a human cannot hear? Do their explanations point at this sound?

## The hypotheses

**H1 (decisions).** Audio models use sound that a human cannot hear. If we remove only the inaudible part of a clip, the answer of the model changes.

**H2 (explanations).** Attribution maps put more weight on inaudible bins than a random map does.

**H3 (codecs).** MP3 and Opus also remove the inaudible part first. Thus a model that depends more on the inaudible part loses more accuracy under these codecs.

## The refuting result

The project is refuted if all these statements are true:

1. For every model and task, the removal of the inaudible part changes the answer of the model no more than a null change does (see below).
2. Statement 1 is true at both playback levels and under both masking models.
3. For every attribution method, the share of the map in inaudible bins is not larger than the share for a random map.

Then the models hear only what a human hears. The result is still useful: the metric becomes a certificate for a model.

## How we decide for one model and one task

A null change is a change that a human cannot hear and that removes no sound. Examples:

- a shift of the clip by a few samples
- a change of the level by 0.5 dB
- noise at -90 dBFS
- resynthesis without a change (STFT and inverse STFT)

The decision has three steps:

1. Measure the change of the model output under each null change. The noise floor of the model is the largest upper limit of the 95 % bootstrap intervals.
2. Measure the change under the removal of the inaudible part, with its 95 % bootstrap interval.
3. Compare the two values:
   - If the upper limit of the removal is below the noise floor, the removal has no effect (the refuting result for this pair).
   - If the lower limit of the removal is above the noise floor, the removal has an effect (H1 for this pair).
   - In all other cases, the result is not clear. Then we add clips.

The main measure is the Jensen-Shannon divergence between the outputs (see `src/inaudible/metrics.py`).

## The role of the between-clip change

The between-clip change is the change of the output between two different clips. We use it only as a scale. We give the effect of the removal as a percentage of the between-clip change. Then the numbers of different models have the same scale. The between-clip change is not a part of the decision.
