# Build sequence

The editable CAD project uses Build123d and preserves the original Fusion geometry and timeline as reference material.

1. [Set up the environment and prepare the wheel scan](README.md#run).
2. Run `./run.sh` to build the unsplit master, including the finishing fillets and zero-added-clearance Sherman P imprint.
3. Run `split_adapter.py` with the same Python environment to create the two printing halves and their five connector recesses.
4. Run `latch.py` to export the separate latch. The [saddlebag mount recipe](docs/ACCESSORY-PARTS.md) remains available as a Fusion reference.
5. Follow the [verification instructions](README.md#verification) to regenerate the scan inspection outputs and validate the model.

The [rebuild guide](docs/CAD-REBUILD.md), [portable recipe](cad-rebuild/recipe.json), and [Fusion timeline](docs/FUSION-TIMELINE.md) record the source geometry and corrections. Run `node scripts/generate-cad-reference.mjs` to regenerate the portable baseline recipe and source tables.
