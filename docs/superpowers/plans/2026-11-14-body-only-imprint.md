# Body-only Sherman P adapter imprint

User correction: subtract only the prepared 1.003-scaled body at approved Y=-191/+170 mm cuts. Keep both original handles visible as separate, stationary reference objects in the viewer. The merged scan remains a historical preparation export and must never be the adapter cutter.

- Add an independent regression using accepted body-scaled STEP and pre-imprint adapter; observe old full-scan subtraction fail.
- Allow preparation without reunion and reuse it in adapter and viewer from original scan.
- Regenerate adapter STEP/STL/preview; run geometry/orientation suite, ceiling validation, export/parameter validation.
- Update current documentation, review and commit locally.

Scale origin remains model (0,0,0); no other manufacturing geometry changes.

Completed: old full-scan regression failed by 10,361.519 mm³ before integration. Current adapter volume 1,517,837.554 mm³ agrees with independent accepted-tool subtraction within 0.001 mm³. Front clip probe (-40,-235,15) retains material. All 12 independent ceiling mesh checks passed; STEP/STL reopened as valid single solids; AirTag 8.6 mm parameter test passed. Viewer refreshed successfully with four separate objects. Independent read-only review found no material issues. STEP writer whitespace is native generated formatting; source/document diff checks pass.
