# SolidCraft seat-adapter project

SolidCraft-specific files stay in this folder. The installed version checked during setup is **0.40.1**.

The native adapter is now built and open in SolidCraft. Open [models/seat-adapter.sc](models/seat-adapter.sc) for the unsplit master and the dependent `AdapterBodySplit` component. The two printing halves are hidden initially, so they do not overlap the visible master. Show the child bodies and hide the master to inspect the split.

The root `seat-adapter` is a container. Its sibling components are `AdapterBody` (master, 20 sketches and its manufacturing features), `AdapterBodySplit` (two printing halves and five connector sketches), and `WheelScanReference` (a hidden display mesh). The shared copy relationship remains a root-level feature. Older checkpoint documents retain their original organization. See [the reorganization record](REORGANIZATION.md).

Verification: 3 closed manufactured solids (one master plus two child halves), a separate hidden reference mesh, 70 timeline entries, 25 fixed sketches, no feature errors or warnings, all 12 mounting-ceiling material checks passed, and a temporary parameter change verified parent-to-child propagation. See [build results and limitations](BUILD-RESULTS.md), [original validation record](logs/build-validation.json), and [reorganization verification](logs/reorganization-validation.json).

This is not an exact Onshape geometry match. One left circular cut uses a 256-sided cutter, retaining its exact circle as construction geometry; maximum radial deviation is 0.001506 mm. Other source-to-target adaptations and the measured volume difference are documented in the build results.

## Connect Codex to the desktop app

The `solidcraft` MCP server is configured in Codex using:

```toml
[mcp_servers.solidcraft]
command = 'C:\Program Files\SolidCraft\solidcraft-cli.exe'
args = ["mcp", "--connect", "127.0.0.1:7878", "--allow-path", 'C:\Projects\Sherman P Seat Adapter\SolidCraft', "--compact"]
```

1. Start SolidCraft with its local control channel enabled. Run `Start-SolidCraft.ps1` from this folder, or use PowerShell:

   ```powershell
   & 'C:\Program Files\SolidCraft\solidcraft.exe' --control 7878
   ```

2. Restart Codex to load the new MCP configuration, then reopen this project/conversation.
3. Ask: **“Connect to SolidCraft, inspect the blank design, then rebuild the seat adapter using SolidCraft/README.md and the portable recipe.”**

The MCP bridge connects to the app on localhost. It does not need an Onshape API key. Keep the app open while it is being controlled. This configuration deliberately names a fixed desktop port rather than opening an unrelated headless design session.

If the app was already open without that port, save any work, close it, and reopen it with the command above. Do not discard an unsaved model just to start the connection.

The setup is configured and tested separately from the model build. An empty directory or a successful MCP handshake does not mean the seat adapter has already been constructed in SolidCraft.

## Project files

| Folder | Purpose |
|---|---|
| `inputs/` | Snapshots of the millimeter rebuild recipe and already aligned wheel scan |
| `models/` | Native `.sc` master/child project files when built |
| `scripts/` | SolidCraft command scripts, automation and connection check |
| `exports/` | STEP/STL/3MF comparison and printing outputs |
| `logs/` | Connection checks, measurements and validation records |

The inputs are snapshots copied from the parent project's authoritative files. If the parent recipe changes, deliberately refresh these copies and their hashes before rebuilding.

## Build scope and replay

Read [the parent CAD guide](../docs/CAD-REBUILD.md), [porting checklist](../docs/PORTING-AND-VALIDATION.md), and `inputs/recipe.json`.

- One unsplit master adapter, including corrected screw ceilings and wheel imprint.
- A linked/dependent printing child, split into two pieces, with five 8 mm connector recesses.
- No fillets, no loose connector inserts, no additional clearance.
- Inputs use millimeters. The supplied scan is already aligned. Do not apply Onshape's historical 0.001 unit correction if SolidCraft imports the STL in millimeters.

The full reproducible command script is [scripts/seat-adapter-build.json](scripts/seat-adapter-build.json). It rebuilds into a separate CLI process and saves a new native document:

```powershell
& 'C:\Program Files\SolidCraft\solidcraft-cli.exe' run scripts/seat-adapter-build.json --save models/seat-adapter.sc
```

Run from this SolidCraft folder. The scan path in the script currently names this Windows project folder; update it if moving the repository. The generator scripts preserve the known SolidCraft workarounds. Diagnostic scripts and experimental snapshots are not the main build entry point.

The separate latch and saddle bag mount have been extracted and documented in [the accessory guide](../docs/ACCESSORY-PARTS.md); neither accessory has been built in SolidCraft yet.

## Optional local connection check

With Node.js installed:

```powershell
node scripts/check-connection.mjs
```

This checks MCP initialization and tool discovery. It also performs a read-only design inspection when the desktop port is reachable. It never creates geometry. Results are written to `logs/connection-check.json`.

Setup references: [SolidCraft MCP documentation](https://docs.solidcraft.io/guide/mcp.html) and [official OpenAI MCP guidance](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).
