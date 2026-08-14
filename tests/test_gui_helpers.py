import pytest
import nmrpeaksim.gui.callbacks as cb
from nmrpeaksim.core.core import Plot
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


# ---------------------------------------------------------------------------
# Splitting slider visibility
# ---------------------------------------------------------------------------

class DpgStub:
    """Models item existence and visibility so slider state is observable."""

    def __init__(self):
        self.shown = {}
        self.children = {'pwi_top': ['pwi_top_title', 'pwi_top_spacer'],
                         'pwi_bottom': ['pwi_bottom_title', 'pwi_bottom_spacer']}
        self.vals = {'peak_select': ''}

    def add_slider_int(self, **kwargs):
        self.shown[kwargs['tag']] = True
        self.children[kwargs['parent']].append(kwargs['tag'])

    def does_item_exist(self, tag):
        return tag in self.shown

    def is_item_shown(self, tag):
        return self.shown.get(tag, False)

    def show_item(self, tag):
        self.shown[tag] = True

    def hide_item(self, tag):
        self.shown[tag] = False

    def get_item_children(self, tag, slot=None):
        return self.children.get(tag, []) if slot is not None else {1: []}

    def get_item_alias(self, tag):
        return tag

    def get_value(self, tag, *args):
        return self.vals.get(tag, '')

    def set_value(self, tag, value):
        self.vals[tag] = value

    def get_item_width(self, *args):
        return 400

    def get_item_height(self, *args):
        return 200

    def __getattr__(self, name):
        return lambda *args, **kwargs: None


class FakeSpectrumData:
    def __init__(self):
        self.spectrum = Plot()
        self.peaks = []
        self.selected_peak = 0


@pytest.fixture
def stub(monkeypatch):
    s = DpgStub()
    monkeypatch.setattr(cb, 'dpg', s)
    return s


def visible(stub):
    return sorted(tag for tag, shown in stub.shown.items() if shown)


def test_sliders_appear_for_each_splitting(stub):
    d = FakeSpectrumData()
    d.spectrum.add_peak(center_shift=1.5)
    d.spectrum.peaks[0].split_peak(mult=2, J=7)
    d.spectrum.peaks[0].split_peak(mult=3, J=3)
    cb.peak_select_update('add_peak', None, d)
    assert visible(stub) == ['coupling1', 'coupling2', 'split1', 'split2']


def test_sliders_hidden_when_splitting_count_drops(stub):
    d = FakeSpectrumData()
    d.spectrum.add_peak(center_shift=1.5)
    d.spectrum.peaks[0].split_peak(mult=2, J=7)
    d.spectrum.peaks[0].split_peak(mult=3, J=3)
    cb.peak_select_update('add_peak', None, d)
    d.spectrum.peaks[0].undo_split()
    cb.peak_select_update('undo_split', None, d)
    assert visible(stub) == ['coupling1', 'split1']


def test_sliders_hidden_when_last_peak_removed(stub):
    d = FakeSpectrumData()
    d.spectrum.add_peak(center_shift=1.5)
    d.spectrum.peaks[0].split_peak(mult=2, J=7)
    cb.peak_select_update('add_peak', None, d)
    d.spectrum.remove_peak(0)
    cb.peak_select_update('remove_peak', None, d)
    assert visible(stub) == []


def test_sliders_return_after_re_adding_a_peak(stub):
    d = FakeSpectrumData()
    d.spectrum.add_peak(center_shift=1.5)
    d.spectrum.peaks[0].split_peak(mult=2, J=7)
    cb.peak_select_update('add_peak', None, d)
    d.spectrum.remove_peak(0)
    cb.peak_select_update('remove_peak', None, d)
    d.spectrum.add_peak(center_shift=2.0)
    d.spectrum.peaks[0].split_peak(mult=2, J=5)
    cb.peak_select_update('add_peak', None, d)
    assert visible(stub) == ['coupling1', 'split1']
