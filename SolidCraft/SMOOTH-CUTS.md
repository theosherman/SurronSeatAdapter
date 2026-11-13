# Smooth side-cut revision

Recovery checkpoint: `fc7f175`. User requested smooth matching side cuts instead of the visible facet edges from the earlier 256-sided workaround.

The native model was edited in place. The old polygon cut was deleted, all 256 line segments were removed from `M17_SeatSideProfile`, and its exact R20 construction circle was retained. The working positive-X analytic cut is followed by `M17_KeepSmoothHalf`, `M17_RemoveOppositeHalf`, and `M17_MirrorSmoothHalf`. The geometry is symmetric at this stage; the asymmetric wheel scan is subtracted afterwards. The split child inherits the result.

Both master and front printing half now have two analytic R20 cylindrical faces with mirrored axes (axis distance error about 2.45e-12 mm). The faceted surface is gone. The master now has 948 faces instead of 1013. Its volume is 1,507,476.065203498 mm³; front half 853,718.2229182002 mm³; rear half 636,139.6010199692 mm³. All three are closed.

Validation passed: 72 healthy timeline entries, 25 fixed sketches, no feature errors/warnings, all 12 mounting-ceiling material tests, and the restored 8.5→8.6→8.5 mm AirTag-pocket inheritance experiment. Source/reference components remain siblings. The master, pre-imprint checkpoint, imprinted checkpoint, full rebuild script and manufactured-part exports were refreshed.

Evidence: `logs/smooth-after.json`, `logs/smooth-verification.json`, `logs/smooth-cut-validation.json`, `logs/smooth-replay-validation.json` and `logs/smooth-cuts-top.png`. Run `node scripts/validate-smooth-cuts.mjs` for the saved verification records. `scripts/replace-faceted-side-cut.json` is a one-time patch for the old document, not a stage to reapply to the updated model. The main generator already builds the corrected history.

Earlier build/reorganization logs remain historical. Their 69/70-feature counts and polygon approximation do not describe the current 72-feature model. Exact parity with the prior Onshape port remains unproven.
