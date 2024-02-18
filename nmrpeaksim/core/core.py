__all__ = ["Peak",
           "Spectrum",
           "Plot"]

import numpy as np
import matplotlib.pyplot as plt
from .utils import *


class Peak:
    def __init__(self,
                 center_shift=1.5,
                 integration=1,
                 field=300):
        self.center_shift = center_shift
        self.integration = integration
        self.field = field
        self.intensities = [[1]]
        self.subpeak_shifts = [[self.center_shift]]
        self.splittings = ['s']
        self.couplings = [0]

    def split_peak(self, mult=2, J=7):
        # J=J/ref
        self.intensities.append([prev * new for prev in self.intensities[-1] for new in Pascals_triangle(mult)])
        # print(self.subpeak_shifts, self.subpeak_shifts[-1])
        # if mult%2==0:
        self.subpeak_shifts.append([(prev * self.field + J * (mult - 1) / 2 - subpeak * J) / self.field
                                    for prev in self.subpeak_shifts[-1]
                                    for subpeak in range(mult)])
        self.splittings.append(mult_map[mult])
        self.couplings.append(J)

        """else:
            self.subpeak_shifts.append([(prev*ref + J*(mult-1)/2 - subpeak*J)/ref
                                     for prev in self.subpeak_shifts[-1]
                                    for subpeak in range(mult)])"""
        #print(self.subpeak_shifts[-1])
        return self

    def undo_split(self):
        self.intensities.pop()
        self.subpeak_shifts.pop()
        self.splittings.pop()
        self.couplings.pop()
        return self

    def shift_center(self, delta=0):
        self.center_shift += delta
        self.subpeak_shifts = [[subshift + delta for subshift in splitting]
                               for splitting in self.subpeak_shifts]
        return self

    def get_subpeaks(self):
        return self.intensities[-1], self.subpeak_shifts[-1]

    def __repr__(self):
        if self.splittings == ['s']:
            return str(self.integration)+'H'\
                   +', '+str(self.center_shift) + ' ppm' \
                   +', '+''.join(self.splittings)
        else:
            splits = sorted(zip(self.splittings[1:], [str(i) for i in self.couplings[1:]]),
                            key=lambda x: x[1], reverse=True)

            return str(self.integration)+'H'\
                   +', '+str(self.center_shift) + ' ppm' \
                   +', '+''.join([r[0] for r in splits])\
                   +', J = '+ ', '.join([r[1] for r in splits])+' Hz'


class Spectrum:
    def __init__(self):
        self.peaks = list()

    def add_peak(self, **kwargs):
        if 'peak' in kwargs.keys():
            self.peaks.append(kwargs['peak'])
        else:
            self.peaks.append(Peak(**kwargs))
        print("ADDED PEAK")
        return self

    def modify(self, ind, method, **kwargs):
        return getattr(self.peaks[ind], method)(**kwargs)

    def replace_peak(self, ind, peak):
        self.peaks[ind] = peak
        return self

    def remove_peak(self, ind):
        # len(self.peaks)>ind>=0
        assert 0 <= ind < len(self.peaks), f"Index {ind} is out of the range [0, {len(self.peaks)})."
        self.peaks = self.peaks[:ind] + self.peaks[ind + 1:]
        return self


class Plot(Spectrum):
    def __init__(self,
                 npts=1e5,
                 ppm_min=0,
                 ppm_max=10,
                 intensity_min=0,
                 intensity_max=None,
                 **kwargs):  # pyplot.plot kwargs
        import matplotlib.pyplot as plt

        super().__init__()
        self.npts = npts
        self.ppm_min = ppm_min
        self.ppm_max = ppm_max
        self.intensity_min = intensity_min
        self.intensity_max = intensity_max
        self.kwargs = kwargs

        self.ppm = np.linspace(ppm_min, ppm_max, int(npts))

    def plot(self, peak_int=None, curve="lorentzian", fwhm=0.004, internal=True, bound=False):
        """
        Parameters:
        curve: str
        "lorentzian", "gaussian", "vline"
        fwhm: float
        """

        self.plotted_peaks = []
        if curve == "gaussian":
            for peak in self.peaks:
                inten, subshifts = peak.get_subpeaks()
                pk = np.sum(np.array([gaussian(self.ppm, subshifts[i], inten[i], fwhm)
                                     for i in range(len(inten))]), axis=0)
                self.plotted_peaks.append(pk/np.sum(pk)*peak.integration)

        elif curve == "vline":
            pass

        else:  # lorenzian default
            for peak in self.peaks:
                inten, subshifts = peak.get_subpeaks()
                pk = np.sum(np.array([lorentzian(self.ppm, subshifts[i], inten[i], fwhm)
                                      for i in range(len(inten))]), axis=0)
                self.plotted_peaks.append(pk/np.sum(pk)*peak.integration)

        if internal:
            for i, peak in enumerate(self.plotted_peaks):
                plt.plot(self.ppm, peak / np.sum(peak) * self.peaks[i].integration, **self.kwargs)
            plt.show()
        else:
            if isinstance(peak_int, int):
                sp = self.peaks[peak_int].get_subpeaks()[1]
                bounds = np.logical_and(sp[0]+4*fwhm > self.ppm, self.ppm > sp[-1]-4*fwhm)
                return self.ppm[bounds], self.plotted_peaks[peak_int][bounds]
            else:
                return self.ppm, np.sum(self.plotted_peaks, axis=0)

    def custom_options(self, methods: list):
        for m in methods: m

    def report_peaks(self):
        pass

    def show_integration(self, ind=0, all=False):
        pass

    def show_mult(self, ind, all=False):
        pass

    def show_couplings(self, ind, all=False):
        pass
