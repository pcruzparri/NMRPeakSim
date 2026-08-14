import pytest
from nmrpeaksim.gui.callbacks import selected_peak_label


class FakeRunData:
    """Stands in for RunData: selected_peak_label only reads these two fields."""

    def __init__(self, peaks, selected_peak):
        self.peaks = peaks
        self.selected_peak = selected_peak


# ---------------------------------------------------------------------------
# selected_peak_label
# ---------------------------------------------------------------------------

def test_returns_label_for_valid_selection():
    d = FakeRunData(['0: 1H, 1.50 ppm, s', '1: 2H, 3.00 ppm, d'], 1)
    assert selected_peak_label(d) == (1, '1: 2H, 3.00 ppm, d')


def test_fresh_launch_has_no_selection():
    # RunData starts as peaks=[] with selected_peak=0, which used to IndexError.
    d = FakeRunData([], 0)
    assert selected_peak_label(d) == (None, '')


def test_all_peaks_removed_has_no_selection():
    # peak_select_update sets selected_peak=None once the last peak is gone.
    d = FakeRunData([], None)
    assert selected_peak_label(d) == (None, '')


def test_index_past_end_has_no_selection():
    d = FakeRunData(['0: 1H, 1.50 ppm, s'], 5)
    assert selected_peak_label(d) == (None, '')


def test_negative_index_has_no_selection():
    d = FakeRunData(['0: 1H, 1.50 ppm, s'], -1)
    assert selected_peak_label(d) == (None, '')


@pytest.mark.parametrize('selected', [0, None, 3, -2])
def test_never_raises_on_empty_peaks(selected):
    d = FakeRunData([], selected)
    ind, label = selected_peak_label(d)
    assert ind is None and label == ''
