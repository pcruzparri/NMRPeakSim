__all__ = ["Pascals_triangle",
           "gaussian",
           "lorentzian",
           "vline",
           "lineshapes",
           "unit_peak_height",
           "mult_map",
           "get_key"]


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


def vline(shifts, heights, baseline=0.0, margin=0.0):
    """Stick spectrum as a single polyline.

    Three points per stick — up, back down to the baseline, then along it to
    the next stick. Two points would draw a diagonal from each stick's top to
    the next stick's base. `margin` pads the ends so a lone stick still spans
    a non-zero range on the x axis.
    """
    x, y = [], []
    if margin:
        x.append(shifts[0] + margin)
        y.append(baseline)
    for shift, height in zip(shifts, heights):
        x.extend([shift, shift, shift])
        y.extend([baseline, height, baseline])
    if margin:
        x.append(shifts[-1] - margin)
        y.append(baseline)
    return np.asarray(x, dtype=float), np.asarray(y, dtype=float)


lineshapes = {
    'gaussian': gaussian,
    'lorentzian': lorentzian,
}

# Peak value of a unit-area lineshape of the given width. Used to give sticks
# the height the curve would have at a chosen linewidth.
unit_peak_height = {
    'gaussian': lambda fwhm: 2.355 / (fwhm * np.sqrt(2 * np.pi)),
    'lorentzian': lambda fwhm: 2 / (np.pi * fwhm),
}


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

def get_key(dct, val):
    # Assumes k,v pair is unique in dct
    return list(dct.keys())[list(dct.values()).index(val)]

