# Approved long cavity implementation plan

**Goal:** Implement the browser-approved long central cavity and symmetric rear side relief in Build123d.

**Architecture:** Replace M19's controlling polygon with the approved sixteen straight segments, a uniform 18.5 mm roof offset and straight downward walls. Cut two mirrored rear corners at the approved model coordinates after placement and before the unchanged wheel subtraction. Keep the latch separate and unchanged. No corrective roof patches or fillets.

**Validation:** Compare the completed native solid to the approved scratch STEP; sample roof-normal remaining thickness, verify side removal, and run native regression, mesh mounting-ceiling and export/parameter checks. Preserve continuous rear bridge and top dovetail; supersede rear-only/middle-filled assertions.

- [x] Add failing acceptance tests for long cavity, roof and rear relief.
- [x] Replace cavity source and add the two rear corner cuts.
- [x] Rebuild and verify manufacturing STEP/STL and unchanged accessories/wheel preparation.
- [x] Update implemented render, current project directions and validation records; commit locally.

Execution: inline in the existing checkout so the user's running browser and CAD paths remain stable. Temporary review artifacts stay in ignored Build123d/tmp. No push authorized in this implementation task.

Verification: 45 regression tests, 12 mounting-ceiling mesh checks, native STEP/STL reopening and AirTag depth edit passed. Native preview parity: zero symmetric difference. Roof: minimum 10 mm at 2,578 sampled locations; no continuous all-surface proof claimed.
