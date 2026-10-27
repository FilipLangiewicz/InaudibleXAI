theme

# Explainable AI: semester projects

## How this works

Read the card, then write a one-page plan: the question, the first experiment, and the result that would end the project early. Write that refuting result down before you run anything at scale. Then build the pipeline on a small slice, run the full experiment, and write it up.

Every project ends with a paper-like document (four to eight pages in a conference template) and a repository that reproduces every number in it. You can use coding agents. You must keep the prompts and the agent sessions that produced code in the repository, read every paper you cite, and produce every number in the paper from a file you made. The team's own listening is a check you run often. None of the projects needs a human study.

Each card gives the question, what is known, the terms, the first steps, the plan, what you deliver, the refuting result, where the paper could go, what you need, and what to watch out for. All five run on one workstation GPU. Two cards name a text variant if your team prefers detectors of machine-generated text. If you get stuck or the plan stops making sense, say so early. Please avoid finding out a day before returning the project that the ground truth was wrong.

## Projects

kind
attribution
audit
benchmark
measurement
verification

open all

5 of 5 projects

## X2

### Explanations of what no one can hear: how much of an audio model's decision, and of its explanation, lies below the masking threshold

Every bin of a spectrogram is either audible or masked by louder neighbours, and the masking threshold from psychoacoustics (the model inside MP3) says which. Deleting all energy below the threshold is a change no listener can hear. You will build the threshold, delete the sub-threshold energy, and measure per model how much of the decision and how much of the attribution mass disappears, across five tasks and three architectures. Then you will test whether that number predicts a model's accuracy drop under codecs, which discard the same energy first, and audit listenable explanations for the share of their audio that nobody can hear.

measurement
course form: own experiment, with a new metric and a software package
compute: one workstation GPU

#### The question

How much of what audio models compute rests on inaudible energy, how much of their explanations points at it, and does inaudible reliance predict a model's robustness to codecs?

#### What is known

Psychoacoustic attacks on speech recognition (2018, 2019) hide perturbations under the masking threshold and succeed, which shows that models respond to energy listeners cannot hear. A 2026 causal analysis finds that a practically inaudible change to one frequency flips an audio classifier's decision in over half the cases. Codec robustness of deepfake detectors (2025) and of provenance attribution (2026) was measured without its cause. Listenable explanations (2022, 2024) return audio the user is meant to hear, with no check that it is audible. A 2026 preprint moves the attribution maps of deepfake detectors with inaudible perturbations. Nobody has measured inaudible reliance as a property of models and of explanations, or linked it to codec robustness.

#### Terms used

masking threshold
: the level, per time-frequency bin, below which a listener cannot hear energy because louder neighbouring sound masks it. Computed by a psychoacoustic model from the signal itself.

sub-threshold deletion
: removing every bin below the threshold and resynthesizing the waveform. By construction the listener hears no change.

inaudible reliance
: the change in a model's output under sub-threshold deletion, and the share of an attribution map's mass in sub-threshold bins.

#### First steps

- Implement the masking threshold (the MPEG psychoacoustic model, or an open implementation you have checked) and confirm on ten clips, by listening, that the sub-threshold deletion is inaudible to the team.
- Run one classifier on 100 clips before and after the deletion and report the output change against the change between two different clips.
- Write down the refuting result.

#### Plan

- Set up five tasks with public models and data: speech recognition (Whisper), speaker verification, sound tagging (the Audio Spectrogram Transformer, PANNs), bird sound classification (BirdNET), and deepfake detection (AASIST, a SONICS detector). Use three architectures where the task has them and 300 clips per task.
- Measure the decision change under sub-threshold deletion per model and task, with the between-clip control and bootstrap intervals, at two stated playback levels and with two masking models.
- Measure the inaudible mass of four attribution methods (Integrated Gradients, Grad-CAM, LRP, occlusion) on the common grid, with a random-map control.
- Measure each model's accuracy drop under MP3 and Opus at three bitrates and test whether inaudible reliance predicts it across models.
- Audit listenable maps: the share of a listenable explanation's energy below the threshold of the mix it is played in. Build an audible-by-construction variant (masks restricted to audible bins) and report its faithfulness cost.
- Release the threshold code, the deletion, the metric and the tables as a package.

#### What you deliver

You deliver an inaudible-reliance number for about fifteen model-and-task pairs and an inaudible-mass number for every explainer on them, the codec-prediction table, the audibility audit of listenable maps with the audible variant, and a package that computes the metric on any model. If the numbers are near zero everywhere, you have shown that these models hear what listeners hear, and the metric becomes a certificate worth reporting.

#### What would refute it

The decision change and the attribution mass below threshold stay within the between-clip control for every model and task, at both playback levels and under both masking models.

#### Where the paper could go

Interspeech. ICASSP. WASPAA. A machine learning venue if the codec prediction holds.

#### What you need

Whisper, a speaker verifier, the Audio Spectrogram Transformer, PANNs, BirdNET, AASIST, a SONICS detector. LibriSpeech, a VoxCeleb test set, ESC-50 or an AudioSet evaluation subset, a bird sound set, ASVspoof 2019, SONICS. An MP3 and Opus encoder. Captum, Zennit. The listenable-maps code. One GPU, inference only.

#### Compute

one workstation GPU

#### Watch out for

A masking model is an approximation and depends on the playback level. State the level, use two masking models and report both. Resynthesis after deletion can add artifacts of its own. Check the deletion by ear on a sample of every task and keep the phase. The bird sound set's licence must allow research use.

#### Read first

- Adversarial Attacks Against Automatic Speech Recognition Systems via Psychoacoustic Hiding ([arXiv:1808.05665](https://arxiv.org/abs/1808.05665))
- Imperceptible, Robust, and Targeted Adversarial Examples for Automatic Speech Recognition ([arXiv:1903.10346](https://arxiv.org/abs/1903.10346))
- I Guess That's Why They Call it the Blues: Causal Analysis for Audio Classifiers ([arXiv:2601.16675](https://arxiv.org/abs/2601.16675))
- Measuring the Robustness of Audio Deepfake Detection under Real-World Corruptions ([arXiv:2503.17577](https://arxiv.org/abs/2503.17577))
- Clean Accuracy Does Not Guarantee Provenance Robustness: A Prospective Codec-Stress Evaluation of Audio Attribution ([arXiv:2609.07981](https://arxiv.org/abs/2609.07981))
- Listen to Interpret: Post-hoc Interpretability for Audio Networks with NMF ([arXiv:2202.11479](https://arxiv.org/abs/2202.11479))
- Listenable Maps for Audio Classifiers ([arXiv:2403.13086](https://arxiv.org/abs/2403.13086))
- Listenable Maps for Zero-Shot Audio Classifiers ([arXiv:2405.17615](https://arxiv.org/abs/2405.17615))
- The Perceived Fragility of Explanations in Audio Models: Manipulation of Attribution with Unchanged Predictions ([arXiv:2606.14466](https://arxiv.org/abs/2606.14466))
- A Framework for Evaluating Faithfulness in Explainable AI for Machine Anomalous Sound Detection ([arXiv:2601.19017](https://arxiv.org/abs/2601.19017))

## Toolbox

You can use any tools you like. Say in the paper what you used. Good starting points: Captum and Zennit for attribution, Quantus for metrics, the audioLIME repository for LIME on audio. Compare maps on one common time-frequency grid so that numbers across models mean the same thing. Give every claim a control (a random map, or a random perturbation of the same size) and report bootstrap intervals over clips. Call a difference a difference only when the intervals say so.

Datasets you can start from: ASVspoof 2019 and 2021, In-the-Wild, PartialSpoof, SONICS, FakeMusicCaps, LibriSpeech, a VoxCeleb test set, ESC-50, a bird sound set, a public MIDI corpus. Models you can start from: AASIST, RawNet2, a wav2vec 2.0 detector, the SONICS detectors, the Audio Spectrogram Transformer, PANNs, Whisper, BirdNET, the listenable-maps code. Check every licence before you download.
