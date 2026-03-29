import pytest
import numpy as np
from nmrpeaksim.core.core import Peak, Spectrum, Plot
from nmrpeaksim.core.utils import Pascals_triangle, lorentzian, gaussian


# ---------------------------------------------------------------------------
# Utils
# ---------------------------------------------------------------------------

def test_pascals_triangle():
    assert Pascals_triangle(1) == [1]
    assert Pascals_triangle(2) == [1, 1]
    assert Pascals_triangle(3) == [1, 2, 1]
    assert Pascals_triangle(4) == [1, 3, 3, 1]
    assert Pascals_triangle(5) == [1, 4, 6, 4, 1]


def test_lorentzian_peak_at_center():
    x = np.array([1.5])
    val = lorentzian(x, x0=1.5, a=1.0, FWHM=0.01)
    # At center: a * 0.5*FWHM / pi / (0.5*FWHM)^2 = a / (pi * 0.5 * FWHM)
    expected = 1.0 / (np.pi * 0.5 * 0.01)
    assert np.isclose(val[0], expected)


def test_gaussian_peak_at_center():
    x = np.array([1.5])
    val = gaussian(x, x0=1.5, a=1.0, FWHM=0.01)
    assert np.isclose(val[0], 1.0)


def test_lorentzian_symmetric():
    x = np.array([1.4, 1.5, 1.6])
    vals = lorentzian(x, x0=1.5, a=1.0, FWHM=0.1)
    assert np.isclose(vals[0], vals[2])


def test_gaussian_symmetric():
    x = np.array([1.4, 1.5, 1.6])
    vals = gaussian(x, x0=1.5, a=1.0, FWHM=0.1)
    assert np.isclose(vals[0], vals[2])


# ---------------------------------------------------------------------------
# Peak — initial state
# ---------------------------------------------------------------------------

def test_singlet_initial_state():
    p = Peak(center_shift=1.5, integration=1, field=300)
    assert p.intensities == [[1]]
    assert p.subpeak_shifts == [[1.5]]
    assert p.splittings == ['s']
    assert p.couplings == [0]
    assert p.center_shift == 1.5
    assert p.integration == 1
    assert p.field == 300


def test_get_subpeaks_returns_last_level():
    p = Peak(center_shift=2.0)
    p.split_peak(mult=2, J=7)
    inten, shifts = p.get_subpeaks()
    assert inten == p.intensities[-1]
    assert shifts == p.subpeak_shifts[-1]


# ---------------------------------------------------------------------------
# Peak — splitting
# ---------------------------------------------------------------------------

def test_split_doublet_count():
    p = Peak(center_shift=1.5, field=300)
    p.split_peak(mult=2, J=7)
    assert len(p.intensities) == 2
    assert len(p.subpeak_shifts) == 2
    assert len(p.intensities[-1]) == 2
    assert len(p.subpeak_shifts[-1]) == 2
    assert p.splittings == ['s', 'd']
    assert p.couplings == [0, 7]


def test_split_doublet_symmetry():
    p = Peak(center_shift=1.5, field=300)
    p.split_peak(mult=2, J=7)
    shifts = p.subpeak_shifts[-1]
    # Both lines should be symmetric around center_shift
    midpoint = (shifts[0] + shifts[1]) / 2
    assert np.isclose(midpoint, 1.5)


def test_split_doublet_separation():
    p = Peak(center_shift=1.5, field=300)
    J = 7
    p.split_peak(mult=2, J=J)
    shifts = p.subpeak_shifts[-1]
    separation_hz = abs(shifts[0] - shifts[1]) * p.field
    assert np.isclose(separation_hz, J, atol=1e-6)


def test_split_triplet_intensities():
    p = Peak(center_shift=1.5, field=300)
    p.split_peak(mult=3, J=5)
    assert p.intensities[-1] == [1, 2, 1]


def test_split_doublet_of_triplet_count():
    p = Peak(center_shift=1.5, field=300)
    p.split_peak(mult=2, J=7)
    p.split_peak(mult=3, J=3)
    assert len(p.intensities[-1]) == 6
    assert len(p.subpeak_shifts[-1]) == 6
    assert p.splittings == ['s', 'd', 't']


def test_split_doublet_of_triplet_intensities():
    p = Peak(center_shift=1.5, field=300)
    p.split_peak(mult=2, J=7)
    p.split_peak(mult=3, J=3)
    assert p.intensities[-1] == [1, 2, 1, 1, 2, 1]


def test_split_levels_accumulate():
    p = Peak()
    p.split_peak(mult=2, J=7)
    p.split_peak(mult=2, J=3)
    p.split_peak(mult=2, J=1)
    assert len(p.intensities) == 4
    assert len(p.subpeak_shifts) == 4
    assert len(p.splittings) == 4


# ---------------------------------------------------------------------------
# Peak — undo_split
# ---------------------------------------------------------------------------

def test_undo_split_removes_last_level():
    p = Peak(center_shift=1.5)
    p.split_peak(mult=2, J=7)
    p.split_peak(mult=3, J=3)
    p.undo_split()
    assert len(p.intensities) == 2
    assert p.splittings == ['s', 'd']
    assert p.couplings == [0, 7]


def test_undo_split_does_not_go_below_singlet():
    p = Peak()
    p.undo_split()  # Should be a no-op on a singlet
    assert p.splittings == ['s']
    assert len(p.intensities) == 1


def test_undo_split_restores_singlet():
    p = Peak(center_shift=2.0)
    p.split_peak(mult=2, J=7)
    p.undo_split()
    assert p.splittings == ['s']
    assert p.intensities == [[1]]
    assert p.subpeak_shifts == [[2.0]]


# ---------------------------------------------------------------------------
# Peak — change_splitting
# ---------------------------------------------------------------------------

def test_change_splitting_last_level():
    p = Peak(center_shift=1.5, field=300)
    p.split_peak(mult=2, J=7)
    p.change_splitting(ind=1, mult=3, J=7)
    assert p.splittings[-1] == 't'
    assert len(p.intensities[-1]) == 3


def test_change_splitting_preserves_downstream():
    p = Peak(center_shift=1.5, field=300)
    p.split_peak(mult=2, J=7)   # level 1: d
    p.split_peak(mult=3, J=3)   # level 2: t
    # Change level 1 from d to t; level 2 (t) should still be present
    p.change_splitting(ind=1, mult=3, J=7)
    assert p.splittings == ['s', 't', 't']
    assert len(p.intensities) == 3
    assert len(p.intensities[-1]) == 9  # 3 * 3


def test_change_splitting_requires_positive_index():
    p = Peak()
    p.split_peak(mult=2, J=7)
    with pytest.raises(AssertionError):
        p.change_splitting(ind=0, mult=2, J=7)


# ---------------------------------------------------------------------------
# Peak — shift_center
# ---------------------------------------------------------------------------

def test_shift_center_moves_all_subpeaks():
    p = Peak(center_shift=1.5, field=300)
    p.split_peak(mult=2, J=7)
    original_shifts = [s for level in p.subpeak_shifts for s in level]
    p.shift_center(0.5)
    new_shifts = [s for level in p.subpeak_shifts for s in level]
    for orig, new in zip(original_shifts, new_shifts):
        assert np.isclose(new, orig + 0.5)


def test_shift_center_updates_center_shift():
    p = Peak(center_shift=1.5)
    p.shift_center(1.0)
    assert np.isclose(p.center_shift, 2.5)


def test_shift_center_zero_is_noop():
    p = Peak(center_shift=2.0)
    p.split_peak(mult=3, J=5)
    before = [list(level) for level in p.subpeak_shifts]
    p.shift_center(0)
    after = [list(level) for level in p.subpeak_shifts]
    assert before == after


# ---------------------------------------------------------------------------
# Spectrum
# ---------------------------------------------------------------------------

def test_spectrum_add_peak():
    s = Spectrum()
    s.add_peak(center_shift=1.0)
    assert len(s.peaks) == 1
    assert isinstance(s.peaks[0], Peak)


def test_spectrum_add_existing_peak():
    s = Spectrum()
    p = Peak(center_shift=3.0)
    s.add_peak(peak=p)
    assert s.peaks[0] is p


def test_spectrum_remove_peak():
    s = Spectrum()
    s.add_peak(center_shift=1.0)
    s.add_peak(center_shift=2.0)
    s.remove_peak(0)
    assert len(s.peaks) == 1
    assert np.isclose(s.peaks[0].center_shift, 2.0)


def test_spectrum_remove_peak_out_of_range():
    s = Spectrum()
    s.add_peak(center_shift=1.0)
    with pytest.raises(AssertionError):
        s.remove_peak(5)


def test_spectrum_modify():
    s = Spectrum()
    s.add_peak(center_shift=1.5)
    s.modify(0, 'split_peak', mult=2, J=7)
    assert s.peaks[0].splittings == ['s', 'd']


# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

def test_plot_peak_returns_arrays():
    p = Plot()
    p.add_peak(center_shift=1.5)
    x, y = p.plot_peak(peak_int=0)
    assert len(x) == len(y)
    assert len(x) > 0


def test_plot_peak_x_range_covers_subpeaks():
    p = Plot(fwhm=0.01)
    p.add_peak(center_shift=1.5)
    p.peaks[0].split_peak(mult=2, J=7)
    x, y = p.plot_peak(peak_int=0)
    shifts = p.peaks[0].subpeak_shifts[-1]
    assert x[0] >= min(shifts) - 1.0
    assert x[-1] <= max(shifts) + 1.0


def test_plot_all_yields_all_peaks():
    p = Plot()
    p.add_peak(center_shift=1.0)
    p.add_peak(center_shift=3.0)
    results = list(p.plot_all())
    assert len(results) == 2


def test_plot_peak_invalid_curve():
    p = Plot()
    p.add_peak(center_shift=1.5)
    with pytest.raises(ValueError):
        p.plot_peak(peak_int=0, curve='triangle')
