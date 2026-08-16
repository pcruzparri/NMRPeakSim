# NMRPeakSim

An interactive simulator for first-order NMR multiplets. You build a spectrum peak by
peak, split each one with J-couplings, and watch the lineshape and the coupling tree
update as you drag the sliders.

It's meant for teaching and for sanity-checking a splitting pattern you're trying to
assign — not for fitting real data.

## Install

On Windows, download `NMRPeakSim.exe` from the
[latest release](https://github.com/pcruzparri/NMRPeakSim/releases/latest) and run it.
Nothing else needed — Python is bundled.

To run from source instead, on any platform, you'll want Python 3.10 or newer:

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
pip install -e .
```

On macOS or Linux the activate line is `source .venv/bin/activate`.

`requirements.txt` holds exact pins for a reproducible environment; `pyproject.toml`
declares looser lower bounds for installing the package alongside other things.

## Run

```bash
nmrpeaksim
```

Or as a module:

```bash
python -m nmrpeaksim.gui.main
```

## The window

Four panels across the top, spectrum along the bottom:

- **Peak View** — the currently selected peak on its own, zoomed to its own width.
- **Coupling Tree** — the splitting tree for that peak, with each level colored, the
  J-couplings marked with arrows, and a Hz scale along the bottom.
- **Splitting / Coupling Controls** — one slider pair per splitting level. The top
  slider sets multiplicity, the bottom sets the coupling constant in Hz. Both redraw
  everything live.
- **Tools** — two tabs. *Peak* creates, removes, splits, and shifts peaks. *Plot*
  controls the point count, linewidth, axis ranges, and zoom.

## How a peak is built

Each `Peak` starts as a singlet and accumulates splitting levels. Every call to
`split_peak(mult, J)` takes the current set of subpeaks and splits each one into `mult`
lines separated by `J` Hz, with intensities from the corresponding row of Pascal's
triangle. Multiplicities from 1 to 9 are supported (s, d, t, q, qnt, sxt, spt, oct, non).

Positions are stored in ppm and converted using the spectrometer frequency, so changing
the field moves the lines in ppm while keeping J fixed in Hz — which is the whole point
of the exercise.

The plotted lineshape is a sum of Lorentzians (or Gaussians) over the subpeaks, scaled
so the area under the curve equals the peak's integration.

Dropping the linewidth to zero gives a stick spectrum instead — the zero-width limit of
either lineshape is a delta at each subpeak. The sticks are drawn at the height the curve
would have at the narrowest linewidth the FWHM control can reach, so switching between
the two changes the representation without rescaling the plot.

## Limitations

This is a **first-order** simulation. Every multiplet is built from independent binomial
splittings, so it won't reproduce second-order effects — no roofing, no leaning, nothing
that shows up when Δδ is comparable to J. Strongly coupled systems will look wrong in a
way the simulation can't warn you about.

Linewidth is a single global FWHM shared by every peak — you can't broaden one resonance
without broadening all of them.

## Development

```bash
pip install -e ".[test]"
pytest
```

The test suite covers the core model (peak construction, splitting, undo, normalization)
and the GUI helpers that don't need a live DearPyGui context. The rendering callbacks are
not covered — those need a display.

To cut a release, bump the version in `pyproject.toml`, then tag the commit to match:

```bash
git tag -a v0.1.0 -m "First release"
git push origin v0.1.0
```

CI builds the Windows executable and publishes it. A tag that doesn't match the version
in `pyproject.toml` fails the build rather than shipping a mislabelled binary.

## Layout

```
nmrpeaksim/
    core/
        core.py      Peak, Spectrum, Plot — the model and lineshape math
        utils.py     Pascal's triangle, lineshapes, multiplicity names
    gui/
        main.py      window construction and the DearPyGui entry point
        callbacks.py handlers, plot updates, coupling tree rendering
tests/
```

