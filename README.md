# NMRPeakSim

Interactive simulator for first-order NMR multiplets. Build a spectrum peak by peak,
split each one with J-couplings, and watch the lineshape and coupling tree update as you
drag the sliders.

Useful for teaching, and for checking a first-order splitting pattern you're trying to assign. 

## Install

On Windows, download `NMRPeakSim.exe` from the
[latest release](https://github.com/pcruzparri/NMRPeakSim/releases/latest) and run it.
Python is bundled, so there's nothing else to install.

To run from source on any platform you need Python 3.10 or newer:

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
pip install -e .
```

On macOS or Linux the activate line is `source .venv/bin/activate`.

`requirements.txt` holds exact pins for a reproducible environment. `pyproject.toml`
declares looser lower bounds so the package can be installed alongside other things.

## Run

```bash
nmrpeaksim
```

Or as a module:

```bash
python -m nmrpeaksim.gui.main
```

## The window

Four panels across the top, spectrum along the bottom.

- **Peak View**: the currently selected peak on its own, zoomed to its own width.
- **Coupling Tree**: the splitting tree for that peak. Each level is colored, the
  J-couplings are marked with arrows, and there is a Hz scale along the bottom.
- **Splitting / Coupling Controls**: one slider pair per splitting level. The top slider
  sets multiplicity, the bottom sets the coupling constant in Hz. Both redraw everything
  live.
- **Tools**: two tabs. *Peak* creates, removes, splits, and shifts peaks. *Plot* controls
  the point count, linewidth, axis ranges, and zoom.
- **Spectrum View**: the full spectrum, with all peaks and their lineshapes. 

## How a peak is built

Each `Peak` starts as a singlet and accumulates splitting levels. Every call to
`split_peak(mult, J)` takes the current set of subpeaks and splits each one into `mult`
lines separated by `J` Hz, with intensities from the corresponding row of Pascal's
triangle. Multiplicities from 1 to 9 are supported (s, d, t, q, qnt, sxt, spt, oct, non). 

Positions are stored in ppm and converted using the spectrometer frequency, so changing
the field moves the lines in ppm while J stays fixed in Hz.

The plotted lineshape is a sum of Lorentzians (or Gaussians) over the subpeaks, scaled so
the area under the curve equals the peak's integration.

Setting the linewidth to zero gives a stick spectrum instead, since the zero-width limit
of either lineshape is a delta at each subpeak. The sticks are drawn at the height the
curve would have at the narrowest linewidth the FWHM control can reach, so the plot does
not rescale when you switch.

## Limitations

This is a **first-order** simulation. Every multiplet is built from independent binomial
splittings, so it will not reproduce second-order effects like roofing or leaning, which
appear when Δδ is comparable to J. Strongly coupled systems will look wrong.

Linewidth is a single global FWHM shared by every peak, so broadening one resonance broadens all of them.

## Development

```bash
pip install -e ".[test]"
pytest
```

The tests cover the core model (peak construction, splitting, undo, normalization) and
the GUI helpers that do not need a live DearPyGui context. The rendering callbacks are
not covered, since those need a display.

To cut a release, bump the version in `pyproject.toml`, then tag the commit to match:

```bash
git tag -a v0.1.0 -m "First release"
git push origin v0.1.0
```

CI builds the Windows executable and publishes it. If the tag does not match the version
in `pyproject.toml` the build fails instead of shipping a mislabelled binary.

## Layout

```
nmrpeaksim/
    core/
        core.py      Peak, Spectrum, Plot: the model and lineshape math
        utils.py     Pascal's triangle, lineshapes, multiplicity names
    gui/
        main.py      window construction and the DearPyGui entry point
        callbacks.py handlers, plot updates, coupling tree rendering
tests/
```
