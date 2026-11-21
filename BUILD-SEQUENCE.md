# Build sequence

The editable CAD project uses Build123d and preserves the original Fusion geometry and timeline as reference material.

After installing the locked Python dependencies, run `scripts/build-release.sh`
to build, check, and package the six printable parts in
`exports/SurronSeatAdapter.zip`. GitHub Actions runs that same build on `main`
and publishes the bundle to GitHub Releases. The ZIP contains STLs at its root,
STEP files under `step/`, and three PNG views per part under `previews/`.

The manual build steps are:

1. [Set up the environment and prepare the wheel scan](README.md#run).
2. Run `./build.sh` to build the unsplit master, including the finishing fillets and zero-added-clearance Sherman P imprint.
3. Run `split_adapter.py` with the same Python environment to create the two printing halves and their three 10 mm connector recesses.
4. Run `latch.py` to export the separate latch. The [saddlebag mount recipe](docs/ACCESSORY-PARTS.md) remains available as a Fusion reference.
5. Run `butterfly_keys.py` to export the two connector keys.
6. Follow the [verification instructions](README.md#verification) to regenerate the scan inspection outputs and validate the model.

The [rebuild guide](docs/CAD-REBUILD.md), [portable recipe](cad-rebuild/recipe.json), and [Fusion timeline](docs/FUSION-TIMELINE.md) record the source geometry and corrections. Run `node scripts/generate-cad-reference.mjs` to regenerate the portable baseline recipe and source tables.
