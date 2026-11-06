"""Adapters for the audio models. A new model needs one short class with this interface."""

from typing import Protocol

import numpy as np


class AudioClassifier(Protocol):
    """A model that takes mono waveforms at its sample rate and returns one logit vector per clip."""

    name: str
    sample_rate: int
    labels: list[str]

    def logits(self, waveforms: list[np.ndarray]) -> np.ndarray: ...


class ASTClassifier:
    """Audio Spectrogram Transformer from Hugging Face (AudioSet labels, 16 kHz)."""

    sample_rate = 16000

    def __init__(self, checkpoint: str, device: str = "cuda", batch_size: int = 16) -> None:
        import torch
        from transformers import ASTFeatureExtractor, ASTForAudioClassification

        self.name = checkpoint
        self.torch = torch
        self.device = device
        self.batch_size = batch_size
        self.extractor = ASTFeatureExtractor.from_pretrained(checkpoint)
        self.model = ASTForAudioClassification.from_pretrained(checkpoint).to(device).eval()
        self.labels = [self.model.config.id2label[i] for i in range(self.model.config.num_labels)]

    def logits(self, waveforms: list[np.ndarray]) -> np.ndarray:
        out = []
        for i in range(0, len(waveforms), self.batch_size):
            batch = [w.astype(np.float32) for w in waveforms[i : i + self.batch_size]]
            feats = self.extractor(batch, sampling_rate=self.sample_rate, return_tensors="pt")
            with self.torch.inference_mode():
                logits = self.model(feats["input_values"].to(self.device)).logits
            out.append(logits.float().cpu().numpy())
        return np.concatenate(out)


def build_model(cfg: dict, device: str) -> AudioClassifier:
    if cfg["name"] == "ast":
        return ASTClassifier(cfg["checkpoint"], device, cfg.get("batch_size", 16))
    raise ValueError(f"unknown model {cfg['name']}")
