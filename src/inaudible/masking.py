"""Masking thresholds for frames of one STFT.

Two models are available, so that each result can be reported under both (project card):

- "mpeg1": MPEG-1 psychoacoustic model 1 (ISO/IEC 11172-3, Annex D). The implementation follows
  Painter and Spanias (2000), section V, and the reference code of toolame (psycho_1.c).
- "lin_abdulla": the threshold of Qin et al. (2019), section 4.1, which follows Lin and Abdulla (2015).

Both models evaluate the threshold on every spectral line, use the same threshold in quiet and
the same calibration of the playback level. Thus a change of the model changes only the masking.
"""

from dataclasses import dataclass, field
from typing import ClassVar

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
class MaskingModel:
    """The common part of the masking models: the frequency grid, the calibration and the loop over frames.

    playback_db is the SPL of a full-scale sine. The threshold depends on it through
    the threshold in quiet and through the level-dependent spreading function.
    """

    name: ClassVar[str] = ""
    sample_rate: int
    n_fft: int = 512
    playback_db: float = 96.0
    freqs: np.ndarray = field(init=False, repr=False)
    z: np.ndarray = field(init=False, repr=False)
    quiet_db: np.ndarray = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.freqs = np.arange(self.n_fft // 2 + 1) * self.sample_rate / self.n_fft
        self.z = bark(self.freqs)
        self.quiet_db = absolute_threshold(self.freqs)

    def to_db(self, power: np.ndarray) -> np.ndarray:
        """Convert a one-sided power spectrum ("spectrum" scaling, Hann window) to dB SPL."""
        return self.playback_db + 10 * np.log10(np.maximum(power, 1e-30) / _HANN_SINE_POWER)

    def frame_threshold(self, x_db: np.ndarray) -> np.ndarray:
        """Global masking threshold in dB SPL for one frame, given its spectrum in dB SPL."""
        raise NotImplementedError

    def threshold(self, power: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Masking threshold for a power spectrogram of shape (lines, frames).

        Returns the spectrogram and the threshold, both in dB SPL.
        """
        x_db = self.to_db(power)
        thr = np.stack([self.frame_threshold(x_db[:, t]) for t in range(x_db.shape[1])], axis=1)
        return x_db, thr


@dataclass
class Model1(MaskingModel):
    """Masking threshold of MPEG-1 psychoacoustic model 1."""

    name: ClassVar[str] = "mpeg1"
    _band: np.ndarray = field(init=False, repr=False)
    _neighbours: list[np.ndarray] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        self._band = np.floor(self.z).astype(int)
        scale = _REFERENCE_LINE_HZ / (self.sample_rate / self.n_fft)
        self._neighbours = []
        for f in self.freqs:
            ref = [2] if f < 5500 else [2, 3] if f < 11000 else [2, 3, 4, 5, 6]
            self._neighbours.append(np.unique(np.maximum(2, np.round(np.array(ref) * scale).astype(int))))

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


@dataclass
class Model2(MaskingModel):
    """Masking threshold of Qin et al. (2019), section 4.1, after Lin and Abdulla (2015).

    All maskers are tonal. A masker is a local maximum of the spectrum that is above the threshold
    in quiet and is the strongest masker within 0.5 Bark. The spread function has two slopes.

    The reference code of Qin et al. (cleverhans, generate_masking_threshold.py) differs from the
    paper in two points. It lowers the threshold in quiet by 12 dB, and it removes the threshold in
    quiet below 1 Bark. This class follows the paper. Qin et al. also scale each clip so that its
    largest bin is at 96 dB. This class uses the fixed calibration of playback_db instead, because
    the project card asks for a stated playback level.
    """

    name: ClassVar[str] = "lin_abdulla"

    def maskers(self, x_db: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Find the maskers of one frame. Returns the line index and the power in dB SPL of each masker."""
        k = np.flatnonzero((x_db[1:-1] > x_db[:-2]) & (x_db[1:-1] > x_db[2:])) + 1
        lin = 10 ** (x_db / 10)
        power = 10 * np.log10(lin[k - 1] + lin[k] + lin[k + 1])
        keep = power >= self.quiet_db[k]
        k, power = k[keep], power[keep]
        # A masker stays if no other masker within 0.5 Bark is stronger. Of two equal maskers, the lower one stays.
        near = np.abs(self.z[k][:, None] - self.z[k][None, :]) < 0.5
        lower = np.arange(len(k))[:, None] < np.arange(len(k))[None, :]
        beats = (power[:, None] > power[None, :]) | ((power[:, None] == power[None, :]) & lower)
        strongest = np.all(~near | beats | np.eye(len(k), dtype=bool), axis=1)
        return k[strongest], power[strongest]

    def frame_threshold(self, x_db: np.ndarray) -> np.ndarray:
        """Global masking threshold in dB SPL for one frame, given its spectrum in dB SPL."""
        idx, power = self.maskers(x_db)
        total = 10 ** (self.quiet_db / 10)
        if len(idx):
            zj = self.z[idx][:, None]
            pj = power[:, None]
            dz = self.z[None, :] - zj
            upper_slope = -27 + 0.37 * np.maximum(pj - 40, 0)
            spreading = np.where(dz <= 0, 27 * dz, upper_slope * dz)
            individual = pj + (-6.025 - 0.275 * zj) + spreading
            total = total + (10 ** (individual / 10)).sum(axis=0)
        return np.asarray(10 * np.log10(total))


MASKING_MODELS: dict[str, type[MaskingModel]] = {m.name: m for m in (Model1, Model2)}


def build_masking(name: str, sample_rate: int, n_fft: int, playback_db: float) -> MaskingModel:
    """Make the masking model of the config ("mpeg1" or "lin_abdulla")."""
    if name not in MASKING_MODELS:
        raise ValueError(f"unknown masking model {name!r}, select one of {sorted(MASKING_MODELS)}")
    return MASKING_MODELS[name](sample_rate, n_fft, playback_db)
