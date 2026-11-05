"""Change of a model output, the between-clip control and bootstrap intervals."""

import numpy as np


def softmax(logits: np.ndarray) -> np.ndarray:
    z = logits - logits.max(axis=-1, keepdims=True)
    e = np.exp(z)
    return np.asarray(e / e.sum(axis=-1, keepdims=True))


def js_divergence(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Jensen-Shannon divergence in bits between softmax(a) and softmax(b), row by row. Range [0, 1]."""
    p, q = softmax(a), softmax(b)
    m = (p + q) / 2

    def kl(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return np.asarray(np.sum(x * (np.log2(np.maximum(x, 1e-30)) - np.log2(np.maximum(y, 1e-30))), axis=-1))

    return np.clip((kl(p, m) + kl(q, m)) / 2, 0.0, 1.0)


def cosine_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """1 minus the cosine similarity of the logit vectors, row by row."""
    num = np.sum(a * b, axis=-1)
    den = np.linalg.norm(a, axis=-1) * np.linalg.norm(b, axis=-1)
    return np.asarray(1 - num / np.maximum(den, 1e-30))


def output_change(a: np.ndarray, b: np.ndarray) -> dict[str, np.ndarray]:
    """All measures of the change between two logit arrays of shape (clips, classes)."""
    return {
        "top1_changed": (a.argmax(axis=-1) != b.argmax(axis=-1)).astype(float),
        "js_divergence": js_divergence(a, b),
        "cosine_distance": cosine_distance(a, b),
    }


def between_clip_pairs(n: int, rng: np.random.Generator) -> np.ndarray:
    """A partner for each clip, never the clip itself: the next clip in a random cyclic order."""
    order = rng.permutation(n)
    partner = np.empty(n, dtype=int)
    partner[order] = np.roll(order, -1)
    return partner


def bootstrap_ci(
    values: np.ndarray, rng: np.random.Generator, n_boot: int = 10000, level: float = 0.95
) -> tuple[float, float, float]:
    """Mean and the percentile bootstrap interval of the mean, with resampling over clips."""
    values = np.asarray(values, dtype=float)
    means = values[rng.integers(0, len(values), size=(n_boot, len(values)))].mean(axis=1)
    lo, hi = np.quantile(means, [(1 - level) / 2, (1 + level) / 2])
    return float(values.mean()), float(lo), float(hi)
