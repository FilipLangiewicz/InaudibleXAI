import numpy as np
import pytest

from inaudible.deletion import analyze, delete_random, delete_subthreshold, noise_to_mask, resynthesize
from inaudible.masking import Model1, absolute_threshold, bark

SR = 44100
N_FFT = 512
T = np.arange(SR) / SR
# A tone at the centre of a line has no leakage beyond the next line of a Hann window.
LOUD_LINE, QUIET_LINE = 12, 15


def tone(line: int, amplitude: float) -> np.ndarray:
    return amplitude * np.sin(2 * np.pi * line * SR / N_FFT * T)


def audible_share(x: np.ndarray, line: int, model: Model1) -> float:
    result = delete_subthreshold(x, model)
    frames = slice(2, -2)
    return float(result.audible[line, frames].mean())


def test_bark_and_quiet_threshold_reference_values():
    assert bark(np.array([1000.0]))[0] == pytest.approx(8.5, abs=0.1)
    assert absolute_threshold(np.array([3300.0]))[0] < -4
    assert absolute_threshold(np.array([100.0]))[0] > 20


def test_full_scale_sine_has_playback_level():
    model = Model1(SR, N_FFT, playback_db=96.0)
    x_db = model.to_db(np.abs(analyze(tone(LOUD_LINE, 1.0), N_FFT)) ** 2)
    power = 10 ** (x_db[LOUD_LINE - 1 : LOUD_LINE + 2, 10] / 10)
    assert 10 * np.log10(power.sum()) == pytest.approx(96.0, abs=0.01)


def test_quiet_tone_near_loud_tone_is_masked():
    model = Model1(SR, N_FFT)
    assert audible_share(tone(QUIET_LINE, 0.005), QUIET_LINE, model) == 1.0
    assert audible_share(tone(LOUD_LINE, 0.5) + tone(QUIET_LINE, 0.005), QUIET_LINE, model) == 0.0
    assert audible_share(tone(LOUD_LINE, 0.5) + tone(QUIET_LINE, 0.005), LOUD_LINE, model) == 1.0


def test_tone_below_threshold_in_quiet_is_deleted():
    # 1e-5 of full scale is near 0 dB SPL at 96 dB playback, below the threshold in quiet at 1.3 kHz.
    model = Model1(SR, N_FFT)
    assert audible_share(tone(QUIET_LINE, 1e-5), QUIET_LINE, model) == 0.0


def test_lower_playback_level_deletes_more():
    rng = np.random.default_rng(0)
    x = 0.05 * rng.standard_normal(SR // 2)
    loud = delete_subthreshold(x, Model1(SR, N_FFT, playback_db=96.0))
    soft = delete_subthreshold(x, Model1(SR, N_FFT, playback_db=60.0))
    assert soft.fraction_bins_deleted > loud.fraction_bins_deleted


def test_threshold_is_not_below_threshold_in_quiet():
    rng = np.random.default_rng(1)
    model = Model1(SR, N_FFT)
    result = delete_subthreshold(0.1 * rng.standard_normal(SR // 4), model)
    assert np.all(result.threshold_db >= model.quiet_db[:, None] - 1e-9)


def test_resynthesis_without_change_is_exact():
    rng = np.random.default_rng(2)
    x = rng.standard_normal(SR // 4)
    assert np.allclose(resynthesize(x, N_FFT), x, atol=1e-10)


def test_deletion_removes_masked_tone_and_is_below_threshold():
    model = Model1(SR, N_FFT)
    x = tone(LOUD_LINE, 0.5) + tone(QUIET_LINE, 0.005)
    result = delete_subthreshold(x, model)
    spec = np.abs(analyze(result.deleted, N_FFT))[:, 4:-4]
    assert spec[QUIET_LINE].max() < 1e-6
    check = noise_to_mask(x, result.deleted, result.threshold_db, model)
    # The abrupt start and end of the tone leave a small audible residual in the edge frames.
    assert check["fraction_bins_audible"] < 0.01


def test_band_check_sums_the_residual_over_each_band():
    # In white noise, each deleted line is below the threshold, but the sum over a wide band is not.
    model = Model1(SR, N_FFT)
    x = 0.2 * np.random.default_rng(4).standard_normal(SR // 2)
    result = delete_subthreshold(x, model)
    check = noise_to_mask(x, result.deleted, result.threshold_db, model)
    assert check["fraction_bins_audible"] < 0.01
    assert check["fraction_bands_audible"] > 0.1
    assert noise_to_mask(x, resynthesize(x, N_FFT), result.threshold_db, model)["fraction_bands_audible"] == 0.0


def test_random_deletion_is_audible():
    rng = np.random.default_rng(3)
    model = Model1(SR, N_FFT)
    x = 0.1 * rng.standard_normal(SR) + tone(LOUD_LINE, 0.3)
    result = delete_subthreshold(x, model)
    random = delete_random(x, result.audible, N_FFT, rng)
    nmr_deleted = noise_to_mask(x, result.deleted, result.threshold_db, model)["nmr_db"]
    nmr_random = noise_to_mask(x, random, result.threshold_db, model)["nmr_db"]
    assert nmr_random > nmr_deleted + 10
