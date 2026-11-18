# Research hypotheses and the refuting result

We wrote these hypotheses on 2026-11-05, before the first run at scale. We can change the decision rules only before the run of all models (T3).

## The question

Do audio models use sound that a human cannot hear? Do their explanations point at this sound?

## The hypotheses

**H1 (decisions).** Audio models use sound that a human cannot hear. If we remove only the inaudible part of a clip, the answer of the model changes.

**H2 (explanations).** Attribution maps put more weight on inaudible bins than a random map does.

**H3 (codecs).** MP3 and Opus also remove the inaudible part first. Thus a model that depends more on the inaudible part loses more accuracy under these codecs.

## The refuting result

We use the refuting result of the project card (`task_input/X2_projekt.md`) without a change:

> The decision change and the attribution mass below threshold stay within the between-clip control for every model and task, at both playback levels and under both masking models.

If this result occurs, the models hear only what a human hears. The result is still useful: the metric becomes a certificate for a model.

## The playback levels and the masking models

The card tells us to state the playback level, to use two levels and to use two masking models. The team set these values on 2026-11-16, before T3.

The playback level is the SPL of a full-scale sine. The config key `masking.playback_db` sets it. Both masking models use the same calibration.

| Level | Source | Reason |
|---|---|---|
| 96 dB SPL | MPEG-1 model 1 (ISO/IEC 11172-3) and Qin et al. (2019). Schönherr et al. (2019) use 95 dB. | This level is the dynamic range of 16-bit audio. The attack papers use it. Thus our deletion uses the same rule as these papers. |
| 92 dB SPL | ITU-R BS.1387 (PEAQ). Kabal (2002), section 2, states this value: "In the absence of other information, BS.1387 indicates that Lp should be set to 92 dB SPL." | This level is the default of the standard for objective audio quality. PEAQ is one of the measures of Kitłowski et al. (2026). |

A lower level gives a higher threshold in quiet relative to the signal. Thus the deletion at 92 dB removes more energy than the deletion at 96 dB.

The two masking models (config key `masking.model`):

| Name | Model | Source |
|---|---|---|
| `mpeg1` | MPEG-1 psychoacoustic model 1 | ISO/IEC 11172-3, Painter and Spanias (2000), toolame (`psycho_1.c`) |
| `lin_abdulla` | The threshold of Qin et al. (2019), section 4.1 | Lin and Abdulla (2015), as Qin et al. describe it |

`src/inaudible/masking.py` describes the differences between the paper of Qin et al. and their code.

## The controls

All controls come from the project card:

- `between_clips`: the change of the output between two different clips (card, "First steps").
- `resynthesis`: STFT and inverse STFT without a change. It shows the artifacts of the resynthesis alone (card, "Watch out for").
- `random_deletion`: the same number of bins per frame, removed at random lines. It is the random perturbation of the same size (card, "Toolbox").
- a random map, for the attribution mass (card, "Plan" and "Toolbox").

Each value has a 95 % bootstrap interval over the clips. We call a difference a difference only when the intervals show it (card, "Toolbox").

The main measure is the Jensen-Shannon divergence between the outputs (see `src/inaudible/metrics.py`).

## How we decide for one model and one task

The card does not give a number for "within the between-clip control". The team set this rule on 2026-11-06, after the 100-clip prototype and before T3:

1. For each clip, measure the change of the output under the deletion and under the between-clip control.
2. Divide the mean deletion change by the mean between-clip change.
3. Compute the 95 % bootstrap interval of this ratio. Each resample uses the same clips for both means.
4. Compare the interval with the margin of 5 %:
   - If the upper limit is below 5 %, the deletion change is within the between-clip control (the refuting result for this pair).
   - If the lower limit is above 5 %, the deletion change is outside the between-clip control (H1 for this pair).
   - In all other cases, the result is not clear. Then we add clips.

The margin of 5 % is a decision of the team. It is the same value as in the first version of this file. The rows `deletion_vs_between` of `summary.csv` give the ratio, its interval and the verdict.

We set the rule for the attribution mass before T4.
