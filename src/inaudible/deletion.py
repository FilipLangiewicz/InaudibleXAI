"""Sub-threshold deletion: remove every STFT bin below the masking threshold and resynthesize.

The deletion keeps the phase of the bins that stay. The same STFT gives the threshold,
the mask and the resynthesis, so the mask and the threshold have the same grid.
"""

from dataclasses import dataclass

import numpy as np
from scipy.signal import istft, stft

from inaudible.masking import Model1


def analyze(x: np.ndarray, n_fft: int) -> np.ndarray:
    """Complex STFT with a Hann window and 50 % overlap. Shape (lines, frames)."""
    _, _, spec = stft(x, window="hann", nperseg=n_fft, noverlap=n_fft // 2)
    return np.asarray(spec)


def synthesize(spec: np.ndarray, n_fft: int, length: int) -> np.ndarray:
    """Inverse of analyze(), cut to the original length."""
    _, x = istft(spec, window="hann", nperseg=n_fft, noverlap=n_fft // 2)
    out = np.zeros(length)
    out[: min(length, len(x))] = x[:length]
    return out


@dataclass
class Deletion:
    """The result of a sub-threshold deletion of one clip."""

    deleted: np.ndarray
    audible: np.ndarray
    spectrum_db: np.ndarray
    threshold_db: np.ndarray

    @property
    def fraction_bins_deleted(self) -> float:
        return float(1 - self.audible.mean())

    @property
    def fraction_energy_deleted(self) -> float:
        power = 10 ** (self.spectrum_db / 10)
        return float(power[~self.audible].sum() / power.sum())


def delete_subthreshold(x: np.ndarray, model: Model1) -> Deletion:
    """Remove all bins of x below the masking threshold of x."""
    spec = analyze(x, model.n_fft)
    x_db, thr = model.threshold(np.abs(spec) ** 2)
    audible = x_db >= thr
    deleted = synthesize(np.where(audible, spec, 0), model.n_fft, len(x))
    return Deletion(deleted, audible, x_db, thr)


def resynthesize(x: np.ndarray, n_fft: int) -> np.ndarray:
    """STFT and inverse STFT without a change. It shows the effect of the resynthesis alone."""
    return synthesize(analyze(x, n_fft), n_fft, len(x))


def delete_random(x: np.ndarray, audible: np.ndarray, n_fft: int, rng: np.random.Generator) -> np.ndarray:
    """Control: in each frame, remove the same number of bins as the deletion, at random lines."""
    spec = analyze(x, n_fft)
    keep = np.ones_like(audible)
    n_lines = audible.shape[0]
    for t, n_removed in enumerate((~audible).sum(axis=0)):
        keep[rng.choice(n_lines, size=n_removed, replace=False), t] = False
    return synthesize(np.where(keep, spec, 0), n_fft, len(x))


def noise_to_mask(
    original: np.ndarray, processed: np.ndarray, threshold_db: np.ndarray, model: Model1
) -> dict[str, float]:
    """Objective audibility check of a change, against the masking threshold of the original.

    The residual (original minus processed) is inaudible in a bin if its power is below the threshold.
    Returns the mean noise-to-mask ratio in dB and the fraction of bins with an audible residual.
    """
    residual = analyze(original - processed, model.n_fft)
    thr = threshold_db
    res_db = model.to_db(np.abs(residual) ** 2)
    nmr = 10 ** ((res_db - thr) / 10)
    return {
        "nmr_db": float(10 * np.log10(nmr.mean())),
        "fraction_bins_audible": float((res_db > thr).mean()),
    }
