import numpy as np
import pytest

from inaudible.metrics import (
    between_clip_pairs,
    bootstrap_ci,
    bootstrap_ratio_ci,
    confidence_drop,
    js_divergence,
    output_change,
    within_control,
)


def test_identical_outputs_have_no_change():
    a = np.random.default_rng(0).standard_normal((5, 10))
    change = output_change(a, a.copy())
    for values in change.values():
        assert np.allclose(values, 0, atol=1e-9)


def test_js_divergence_is_one_bit_for_disjoint_outputs():
    a = np.array([[100.0, -100.0]])
    b = np.array([[-100.0, 100.0]])
    assert js_divergence(a, b)[0] == pytest.approx(1.0, abs=1e-6)


def test_confidence_drop_follows_the_top1_class_of_the_first_output():
    a = np.array([[0.0, 10.0]])
    b = np.array([[0.0, 0.0]])
    assert confidence_drop(a, b)[0] == pytest.approx(1 / (1 + np.exp(-10)) - 0.5)
    assert confidence_drop(b, a)[0] == pytest.approx(0.0)


def test_between_clip_pairs_never_pair_a_clip_with_itself():
    rng = np.random.default_rng(0)
    for n in [2, 3, 100]:
        partner = between_clip_pairs(n, rng)
        assert np.all(partner != np.arange(n))
        assert sorted(partner) == list(range(n))


def test_bootstrap_interval_contains_the_mean():
    values = np.random.default_rng(1).standard_normal(200)
    mean, lo, hi = bootstrap_ci(values, np.random.default_rng(2), n_boot=2000)
    assert lo < mean < hi
    assert hi - lo == pytest.approx(2 * 1.96 / np.sqrt(200), rel=0.3)


def test_bootstrap_ratio_of_proportional_values_is_exact():
    den = np.random.default_rng(3).uniform(0.5, 1.0, 100)
    ratio, lo, hi = bootstrap_ratio_ci(0.1 * den, den, np.random.default_rng(4), n_boot=500)
    assert ratio == pytest.approx(0.1)
    assert lo == pytest.approx(0.1) and hi == pytest.approx(0.1)


def test_within_control_needs_the_whole_interval_on_one_side_of_the_margin():
    assert within_control(0.01, 0.04, 0.05) == "within"
    assert within_control(0.06, 0.20, 0.05) == "outside"
    assert within_control(0.03, 0.07, 0.05) == "unclear"
