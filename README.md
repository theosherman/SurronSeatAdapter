# Surron Seat Adapter

## [🧊 Open the interactive 3D preview](https://theosherman.github.io/SurronSeatAdapter/)

An editable Build123d adapter for fitting a Luna Surron seat to a Sherman P.
The project builds an unsplit master, a two-piece printing variant with
butterfly keys, and a separate latch.

## Download

Get `SurronSeatAdapter.zip` from the [latest CAD release](https://github.com/theosherman/SurronSeatAdapter/releases/latest).
The ZIP contains six printable STLs at its root, matching STEP solids under
`step/`, and three PNG views per part under `previews/`. Previous builds are
available in the [release history](https://github.com/theosherman/SurronSeatAdapter/releases).

## Two-piece printing variant

Use the split front and rear STLs with one top butterfly key, two copies of the
cavity key, and the separate latch. The keys have 1 mm fillets on every edge
and match the recess sidewalls with zero nominal CAD clearance. The full
adapter STL is the one-piece alternative. Check brim and support clearance in
your slicer. At the saved
Bambu Studio tilt with independent in-plane rotations, the split footprints
were approximately 245.3 × 245.2 mm front and 200.6 × 200.6 mm rear. The
[historical slicer project](reference/slicer/adapter-body.3mf) preserves an
earlier model and its settings.

The current design lowers the seat 20 mm relative to the printed 8 mm revision.
Physical clip fit and printed strength still need verification.

## Run

Install the locked dependencies with Python 3.14:

```bash
python3.14 -m pip install --user -r requirements.lock.txt
./build.sh --preview
```

Open `exports/preview.html` in a WebGL 2 browser. Use `./build.sh` to include
both adapter variants in the viewer. GitHub Actions builds and publishes the
printable ZIP.
See the [build guide](BUILD-SEQUENCE.md) for all build and validation commands
and the [viewer guide](docs/CAD-VIEWERS.md) for controls and VS Code setup.

## CAD sources

- [CAD rebuild and source map](docs/CAD-REBUILD.md) for editable geometry, coordinate frames, and the portable Fusion baseline.
- [Wheel and seat preparation](docs/WHEEL-REFERENCE-PREPARATION.md) for rebuilding checked-in scan assets.
- [Accessory recipes](docs/ACCESSORY-PARTS.md) for the separate latch and reference-only saddlebag mount.
- [Design history](docs/DESIGN-HISTORY.md) for approved revisions, illustrations, and historical validation.
