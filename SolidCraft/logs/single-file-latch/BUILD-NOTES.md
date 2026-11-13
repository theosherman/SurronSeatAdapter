# Native single-file latch

Authoritative design: `SolidCraft/models/seat-adapter.sc`. Latch is a sibling component and a separate manufactured solid, at identity placement. No master extraction or linked-design import was used. The existing 72 features were retained; the latch adds nine native timeline entries (two sketches and seven solid features).

Measured nominal latch: 230819.78624755502 mm³; source 230819.7862464548 mm³. All source-stage volumes and final bounds agree within the plan tolerances. Adapter master/front/rear volumes remain exactly their live pre-build values. `geometry.json` contains measured bodies, full feature health, component ownership, shared-sketch slot definition and face topology.

## Construction adaptations

- Source stage 102 uses a 120 mm +X extrusion followed by the exact oblique limiting-plane split. Reverse the plane normal so the retained portion containing X=0 keeps the stable Latch body name. The discarded portion is `Latch (1)`. Half volume: 161420.26040547708 mm³. The initial plane orientation and failed rename are diagnostic attempts, not final features.
- Source stage 105 directly consumes sketch 9, `M06_RearDovetailProfile`, in the AdapterBody component. Its selected curve loop remains a native dependency; there is no copied outline or helper interface solid. The 300 mm slot cut passes beyond the specified Y=-263.445982162752 cap, but all Latch material lies at Y >= -222.424548470. Truncating the tool at that cap cannot change the resulting Latch. Stage 105 volume matches the bounded source cut to approximately 0.0000011 mm³.
- Source stage 106 applies `-latchClearance` to the three source mating faces; nominal positive parameter is 0.2 mm. No fillet was built.

`seat-adapter-build.json` reproduces the earlier adapter, not this appended latch. To reproduce the latch, start with the pre-latch native assembly checkpoint and run the builder stages `half`, `blank`, `top`, `slot`, `clearance`, `show` in order. The half stage refuses an existing Latch component. Run from the repository root. Rebuild the saved native design to retain current app edits; do not replay the older adapter generator over it.

`check-single-file-latch.mjs` creates disposable cache-free copies, checks changed/restored shared-sketch edits, zero/nominal clearance, fresh R20/ceiling results and STEP/STL reimports. It does not alter the live document. Fresh results belong in `integration.json`; its absence means integration has not passed. Physical print fit has not been tested.
