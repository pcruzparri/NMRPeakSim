__all__ = ["Pascals_triangle",
           "gaussian",
           "lorentzian",
           "vline",
           "mult_map"]

import numpy as np


def Pascals_triangle(n):
    ind = 1
    row = [0, 1, 0]
    while ind < n:
        row = [0] + [sum(row[i:i+2]) for i in range(len(row)-1)] + [0]
        ind += 1
    return row[1:-1]


def gaussian(x, x0, a, FWHM):
    sigma = FWHM/2.355
    return a * np.exp(-(x-x0)**2/(2*sigma**2))


def lorentzian(x, x0, a, FWHM):
    return a*0.5*FWHM/np.pi/((x-x0)**2 + (0.5*FWHM)**2)


def vline(x, ymin, ymax, npts=100):
    return [x, x], [ymin, ymax]


mult_map = {
    1: 's',
    2: 'd',
    3: 't',
    4: 'q',
    5: 'qnt',
    6: 'sxt',
    7: 'spt',
    8: 'oct',
    9: 'non'
}
