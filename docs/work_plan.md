# Work plan of the team

This file divides the work of T2 to T10 between the three team members. The schedule comes from `docs/design_proposal.md`. Each task has a GitHub issue (#5 to #31). The issues show the relations between the tasks ("blocked by"). An issue without a "blocked by" relation can start at any time.

Status: 2026-11-14.

## Rules of the division

- Each member owns tasks and models. The owner of a task does these steps for the task:
  1. Check the licence of the dataset.
  2. Make the list of 300 clips.
  3. Check the deletion by ear on a sample.
  4. Run the jobs on Kaggle.
- The division agrees with the packages of the literature review (issues #2, #3 and #4).
- All jobs use the Kaggle account `rozaliachojnacka`.

| Member | Literature | Tasks and models |
|---|---|---|
| Joanna | package A | Speech deepfake: AASIST, XLS-R + AASIST. Music deepfake: SpecTTTra. Speaker verification: ECAPA-TDNN, ResNet34, WavLM-sv. |
| Mikołaj | package B | Sound tagging: AST, PANNs, BEATs. Birds: BirdNET, AST-BirdSet, Wav2Vec2-BirdSet. |
| Filip | package C | ASR: Whisper, wav2vec 2.0, Conformer. Masking model 2 and the playback levels. |

## Changes to the schedule

- T2 ends on 2026-11-18.
- T3 is shorter: 2026-11-19 to 2026-11-22.
- All other weeks keep the dates of `docs/design_proposal.md`.

## Week by week

| Week | Dates | Joanna | Mikołaj | Filip |
|---|---|---|---|---|
| T2 | 09.11–18.11 | #5 Model interface for outputs other than logits (text, embeddings, scores). Measures of the output change: WER, score change, EER. #6 Licences and clip lists of ASVspoof 2019 and SONICS. | #7 ABX listening tool and ABX test on ESC-50 (20 to 40 trials, all members listen). #8 Adapters of PANNs and BEATs. | #9 Masking model 2 (Lin and Abdulla). #10 Second playback level, selected from the literature. #11 Objective audibility measures (PEAQ or ViSQOL). |
| T3 | 19.11–22.11 | #13 Adapters and jobs on 300 clips: deepfake and speaker verification. | #14 Adapters and jobs on 300 clips: sound tagging and birds. | #15 Adapters and jobs on 300 clips: ASR. #12 Config grid of 2 playback levels and 2 masking models for all models. |
| T4 | 23.11–29.11 | #20 Occlusion. Random-map control. #17 Decision rule for the attribution mass (before the T4 runs). | #18 IG and Grad-CAM (Captum). #16 Common time-frequency grid. | #19 LRP (Zennit) and AttnLRP. |
| T5 | 30.11–06.12 | #21 Codec pipeline: MP3 and Opus at 3 bitrates (ffmpeg). Codec jobs: deepfake and speaker verification. | #22 Codec jobs: sound tagging and birds. | #23 Codec jobs: ASR. |
| T6 | 07.12–13.12 | #24 Codec prediction: inaudible reliance against the accuracy drop, over the models (bootstrap). | #25 Audit of the listenable maps (L-MAC). Variant with audible bins only. The decoders are an open decision. | #26 Package: CLI, MkDocs, tox (Python 3.11 and 3.12). |
| T7 | 14.12–20.12 | #27 Paper skeleton: results, statistics, H3. | #28 Paper skeleton: explanation methods, H2, listenable maps. | #29 Paper skeleton: psychoacoustics, deletion, related work. #26 Release preparation. |
| T8 | 21.12–27.12 | Break. | Break. | Break. |
| T9 | 28.12–03.01 | #27 Full draft: results. | #28 Full draft: discussion. | #26 Release v1.0.0 with documentation and tests. |
| T10 | 04.01–10.01 | #27 Final edit of the paper. | #30 Video of 3 to 5 minutes. | #31 Final presentation. |

## Work of all members

- Listen to the deletion of each task. The listener is not the person who plays the clips.
- Write a note `notes/YYYY-MM-DD.md` after each step of work.
- Attend the weekly standup.
- Run `just sessions` before each commit with code from an agent session.

## Open decisions

- The rule for a model that does not operate before the end of T3.
- The decoders of T6 (optional, 8 to 16 GPU hours).
