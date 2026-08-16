NMRPeakSim simulates first-order NMR multiplets. Build a spectrum peak by peak, split
each one with J-couplings, and watch the lineshape and coupling tree update as you drag
the sliders.

## Download

`NMRPeakSim.exe` below is a standalone Windows build. Python is bundled, so there is
nothing to install. On other platforms, run from source (see the README).

Windows SmartScreen will probably warn that the publisher is unknown, since the
executable is not code-signed. "More info", then "Run anyway".

## Known limits

- First-order only. Roofing and leaning are not reproduced, so strongly coupled systems
  will look wrong and nothing will warn you.
- Linewidth is a single global FWHM shared by every peak.
- Windows is the only prebuilt target.

---
