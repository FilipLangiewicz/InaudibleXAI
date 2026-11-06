"""MPEG-1 psychoacoustic model 1 (ISO/IEC 11172-3, Annex D).

The implementation follows the description in Painter and Spanias (2000), section V,
and the reference code of toolame (psycho_1.c). It evaluates the threshold on every
spectral line, not on the subsampled frequency grid of the standard.
"""

from dataclasses import dataclass, field

import numpy as np

# The one-sided power sum of a full-scale sine under a Hann window with "spectrum" scaling
# (|sum(w x e)| / sum(w))^2 is 3/8 for every frequency. This value calibrates the dB SPL scale.
_HANN_SINE_POWER = 3.0 / 8.0
# The tonal neighbourhood of the standard is in lines of a 512-point FFT at 44.1 kHz.
_REFERENCE_LINE_HZ = 44100.0 / 512.0


def bark(freq_hz: np.ndarray) -> np.ndarray:
    """Critical band rate (Zwicker) in Bark."""
    f = np.asarray(freq_hz, dtype=float)
    return 13.0 * np.arctan(0.00076 * f) + 3.5 * np.arctan((f / 7500.0) ** 2)


def absolute_threshold(freq_hz: np.ndarray) -> np.ndarray:
    """Threshold in quiet (Terhardt) in dB SPL. Frequencies below 20 Hz use the value at 20 Hz."""
    f = np.maximum(np.asarray(freq_hz, dtype=float), 20.0) / 1000.0
    return 3.64 * f**-0.8 - 6.5 * np.exp(-0.6 * (f - 3.3) ** 2) + 1e-3 * f**4


def _spreading(dz: np.ndarray, power_db: np.ndarray) -> np.ndarray:
    """Spreading function of model 1 in dB. dz is maskee minus masker in Bark."""
    p = np.broadcast_to(power_db, dz.shape)
    sf = np.full(dz.shape, -np.inf)
    m = (dz >= -3) & (dz < -1)
    sf[m] = 17 * dz[m] - 0.4 * p[m] + 11
    m = (dz >= -1) & (dz < 0)
    sf[m] = (0.4 * p[m] + 6) * dz[m]
    m = (dz >= 0) & (dz < 1)
    sf[m] = -17 * dz[m]
    m = (dz >= 1) & (dz < 8)
    sf[m] = (0.15 * p[m] - 17) * dz[m] - 0.15 * p[m]
    return sf


@dataclass
class Model1:
    """Masking threshold of MPEG-1 psychoacoustic model 1 for frames of one STFT.

    playback_db is the SPL of a full-scale sine. The threshold depends on it through
    the threshold in quiet and through the level-dependent spreading function.
    """

    sample_rate: int
    n_fft: int = 512
    playback_db: float = 96.0
    freqs: np.ndarray = field(init=False, repr=False)
    z: np.ndarray = field(init=False, repr=False)
    quiet_db: np.ndarray = field(init=False, repr=False)
    _band: np.ndarray = field(init=False, repr=False)
    _neighbours: list[np.ndarray] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.freqs = np.arange(self.n_fft // 2 + 1) * self.sample_rate / self.n_fft
        self.z = bark(self.freqs)
        self.quiet_db = absolute_threshold(self.freqs)
        self._band = np.floor(self.z).astype(int)
        scale = _REFERENCE_LINE_HZ / (self.sample_rate / self.n_fft)
        self._neighbours = []
        for f in self.freqs:
            ref = [2] if f < 5500 else [2, 3] if f < 11000 else [2, 3, 4, 5, 6]
            self._neighbours.append(np.unique(np.maximum(2, np.round(np.array(ref) * scale).astype(int))))

    def to_db(self, power: np.ndarray) -> np.ndarray:
        """Convert a one-sided power spectrum ("spectrum" scaling, Hann window) to dB SPL."""
        return self.playback_db + 10 * np.log10(np.maximum(power, 1e-30) / _HANN_SINE_POWER)

    def maskers(self, x_db: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Find the tonal and noise maskers of one frame after decimation.

        Returns the line index, the power in dB SPL and a flag (True for tonal) of each masker.
        """
        n = len(x_db)
        tonal_idx: list[int] = []
        for k in range(1, n - 1):
            if not (x_db[k] > x_db[k - 1] and x_db[k] >= x_db[k + 1]):
                continue
            nb = self._neighbours[k]
            nb = np.concatenate([k - nb, k + nb])
            nb = nb[(nb >= 0) & (nb < n)]
            if np.all(x_db[k] - x_db[nb] >= 7):
                tonal_idx.append(k)
        lin = 10 ** (x_db / 10)
        tonal = np.array(tonal_idx, dtype=int)
        tonal_db = np.array([10 * np.log10(lin[k - 1 : k + 2].sum()) for k in tonal])

        # Noise maskers: the lines that are not near a tonal masker, summed in each critical band.
        rest = lin.copy()
        for k in tonal:
            w = int(self._neighbours[k].max())
            rest[max(0, k - w) : k + w + 1] = 0
        noise_idx, noise_db = [], []
        for b in np.unique(self._band):
            lines = np.flatnonzero(self._band == b)
            total = rest[lines].sum()
            if total <= 0:
                continue
            centre = np.exp(np.mean(np.log(np.maximum(lines, 1))))
            noise_idx.append(int(np.clip(np.round(centre), lines[0], lines[-1])))
            noise_db.append(10 * np.log10(total))

        idx = np.concatenate([tonal, np.array(noise_idx, dtype=int)])
        power = np.concatenate([tonal_db, np.array(noise_db)])
        is_tonal = np.concatenate([np.ones(len(tonal), bool), np.zeros(len(noise_idx), bool)])

        # Decimation: remove maskers below the threshold in quiet, then the weaker one of two maskers within 0.5 Bark.
        keep = power >= self.quiet_db[idx]
        idx, power, is_tonal = idx[keep], power[keep], is_tonal[keep]
        order = np.argsort(idx, kind="stable")
        idx, power, is_tonal = idx[order], power[order], is_tonal[order]
        alive = np.ones(len(idx), bool)
        i = 0
        while i < len(idx):
            if not alive[i]:
                i += 1
                continue
            j = i + 1
            while j < len(idx) and not alive[j]:
                j += 1
            if j < len(idx) and self.z[idx[j]] - self.z[idx[i]] < 0.5:
                if power[j] > power[i]:
                    alive[i] = False
                    i = j
                else:
                    alive[j] = False
                continue
            i = j
        return idx[alive], power[alive], is_tonal[alive]

    def frame_threshold(self, x_db: np.ndarray) -> np.ndarray:
        """Global masking threshold in dB SPL for one frame, given its spectrum in dB SPL."""
        idx, power, is_tonal = self.maskers(x_db)
        total = 10 ** (self.quiet_db / 10)
        if len(idx):
            zj = self.z[idx][:, None]
            pj = power[:, None]
            dz = self.z[None, :] - zj
            offset = np.where(is_tonal, -0.275 * self.z[idx] - 6.025, -0.175 * self.z[idx] - 2.025)[:, None]
            individual = pj + offset + _spreading(dz, pj)
            total = total + (10 ** (individual / 10)).sum(axis=0)
        return np.asarray(10 * np.log10(total))

    def threshold(self, power: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Masking threshold for a power spectrogram of shape (lines, frames).

        Returns the spectrogram and the threshold, both in dB SPL.
        """
        x_db = self.to_db(power)
        thr = np.stack([self.frame_threshold(x_db[:, t]) for t in range(x_db.shape[1])], axis=1)
        return x_db, thr
