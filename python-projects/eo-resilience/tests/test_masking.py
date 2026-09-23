import numpy as np
import pytest

from eo_resilience import masking


def test_scl_mask_drops_cloud_shadow_and_cirrus():
    scl = np.array([[4, 5], [3, 10]], dtype="uint8")
    valid = masking.scl_mask(scl)
    assert valid.tolist() == [[True, True], [False, False]]


def test_scl_mask_honours_a_custom_class_list():
    scl = np.array([[4, 6]], dtype="uint8")
    assert masking.scl_mask(scl, invalid=(6,)).tolist() == [[True, False]]


def test_scl_mask_rejects_floats():
    with pytest.raises(TypeError):
        masking.scl_mask(np.zeros((2, 2), dtype="float32"))


def test_qa60_reads_the_two_cloud_bits():
    qa = np.array([[0, 1 << 10], [1 << 11, (1 << 10) | (1 << 11)]], dtype="uint16")
    assert masking.qa60_mask(qa).tolist() == [[True, False], [False, False]]


def test_qa60_ignores_bits_that_are_not_cloud_flags():
    qa = np.array([[1, 1 << 9]], dtype="uint16")
    assert masking.qa60_mask(qa).all()


def test_apply_mask_fills_every_band_of_a_stack():
    bands = np.ones((3, 2, 2), dtype="float32")
    valid = np.array([[True, False], [True, True]])
    out = masking.apply_mask(bands, valid)
    assert out.shape == (3, 2, 2)
    assert np.isnan(out[:, 0, 1]).all()
    assert np.isfinite(out[:, 0, 0]).all()


def test_apply_mask_refuses_a_mask_of_the_wrong_shape():
    with pytest.raises(ValueError):
        masking.apply_mask(np.ones((2, 2)), np.ones((3, 3), dtype=bool))


def test_valid_fraction_counts_usable_pixels():
    valid = np.array([[True, False], [True, True]])
    assert masking.valid_fraction(valid) == pytest.approx(0.75)
