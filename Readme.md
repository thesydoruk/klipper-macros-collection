# Klipper Macro Collection

A modular set of Klipper macros focused on reliability, clear configuration, and predictable print lifecycle behavior.

---

## Macros overview

### `globals.cfg`

Central variables (`_macro_globals`) and `[include …]` for the rest of the collection. **Include this file** from `printer.cfg`:

```ini
[include globals.cfg]
```

### Included when you load `globals.cfg`

| File | Role |
|------|------|
| `print_start.cfg` | `PRINT_START` — homing, mesh/tilt, purge, heat sequencing. |
| `print_end.cfg` | `PRINT_END` — park, retract, cooldown helpers. |
| `state_guard.cfg` | Wraps `PRINT_START` / `PRINT_END` / `PAUSE` / `RESUME` / `CANCEL_PRINT` for `GLOBAL_STATE` and pause-park restore (`_PAUSE_PARK_STATE`). |
| `filament.cfg` | `LOAD_FILAMENT`, `UNLOAD_FILAMENT`, `M701`, `M702`; `PAUSE_AFTER_D` (`AFTER=NONE`, `UNLOAD`, `REMIND`). |
| `layers.cfg` | Layer hooks: `BEFORE_LAYER_CHANGE`, `AFTER_LAYER_CHANGE`, `GCODE_AT_LAYER`, `INIT_LAYER_GCODE` / `RESET_LAYER_GCODE`, pauses/speed/flow per layer. Needs `[display_status]`. |
| `pid.cfg` | `PID_ALL` — autotune all `[extruder*]` heaters and `heater_bed`. |
| `lock_accel.cfg` | `LOCK_ACCEL` / `UNLOCK_ACCEL`; overrides `SET_VELOCITY_LIMIT` (accel lock). |
| `lock_fan.cfg` | Protects a chosen fan from slicer overrides. |
| `velocity.cfg` | Marlin-style `M201` / `M203` / `M205` / `M900` and `RESET_VELOCITY_LIMITS` → `SET_VELOCITY_LIMIT` / `SET_PRESSURE_ADVANCE` (uses `variable_pressure_advance_scale`). |
| `optional/print_checkpoint.cfg` | SD bookmarks + optional recovery (see below). |

### Optional files (include yourself)

These live under `optional/` and are **not** pulled in by `globals.cfg` unless you add another `[include …]`:

- `optional/z_tilt_adjust.cfg` — `Z_TILT_ADJUST`
- `optional/quad_gantry_level.cfg` — `QUAD_GANTRY_LEVEL`
- `optional/test_speed.cfg` — `TEST_SPEED`
- `optional/autotune_sgthrs.cfg` — `AUTOTUNE_SGTHRS_PHASE`

---

## Kinematics reference (toolhead motion)

**Policy:** Any new or changed macro in `*.cfg` must update this section. See `.cursor/rules/gcode-kinematics-doc.mdc` for the checklist.

Conventions used below: **absolute** = `G90` unless noted; **relative** = `G91`. **E** = extruder only on `G1 E…` lines. Where a macro only changes limits/heaters/fans or runs nested commands (`PID_CALIBRATE`, `BED_MESH_CALIBRATE`, `Z_TILT_ADJUST`), the **printed** path is whatever those Klipper built-ins do on your machine; this section lists **explicit** `G`/`M` motion from these repo macros.

### `globals.cfg` / `_macro_globals`

No moves (variables only).

### `print_start.cfg` — body of `_USER_PRINT_START` (`PRINT_START`)

1. `G90`, `M83` (relative extrusion for purge block).
2. `G28` — full homing (all axes per printer config).
3. If mesh bounds set and **probe_eddy_ng**: `G1 Z10 F900`, `G1 X/Y` to mesh centre `F6000`, then `PROBE_EDDY_NG_TAP` / `EDDYNG_BED_MESH_EXPERIMENTAL` (motion per probe stack).
4. Else if mesh set: `BED_MESH_CALIBRATE` (or adaptive) — probe path per mesh config.
5. If `ext_temp > 0`: no XYZ in this phase (heat only).
6. **Purge** (if `can_extrude`, width OK, `purge_length > 0`): `G92 E0`, `G1 Z2 F900`, `G1` to purge corner `F6000`, `G1 Z` = purge layer height `F300`, prime `G1 E… F300`, then alternating `G1 X` lines along Y stepping `+0.4 mm` per line with `E` and purge feedrate; `G92 E0` at end.
7. Optional `INIT_LAYER_GCODE` — no motion unless that macro adds it.

### `print_end.cfg` — `_USER_PRINT_END` (`PRINT_END`)

If **XYZ homed**: `G91`; `G1 E-{retract}` `F1800`; `G1 Z+{lift_z}` `F900`; `G90`; `G1 X{park_x} Y{park_y} F6000`. If not homed: skip retract/lift/park (message only), `G90`. No motion in cooldown/reset phases (`BED_MESH_CLEAR`, fan/heat off, `M220`/`M221`, `RESET_LAYER_GCODE`, `DISABLE_PRINT_CHECKPOINT`, optional `PROBE_EDDY_NG_SET_TAP_OFFSET`).

### `state_guard.cfg`

| Macro | Motion beyond nested call |
|--------|---------------------------|
| `PRINT_START` / `PRINT_END` wrappers | None — forward to `_USER_*`. |
| `PAUSE` | After `_USER_PAUSE` + `M400`: if XYZ homed and pause lift is positive: `G91`, `G1 Z+lift` at `variable_pause_lift_feedrate`, `G90`; then `G1 X/Y` to pause park at `variable_pause_park_feedrate`. If not homed: no move (still saves XYZ to `_PAUSE_PARK_STATE` for info). |
| `RESUME` | If `_PAUSE_PARK_STATE.pending` and paused and XYZ homed: `G90`, `G1` to saved X/Y at pause-park feedrate, then `G1` to saved Z at lift feedrate; clear `pending`. Then `_USER_RESUME` (stock: `RESTORE_GCODE_STATE NAME=PAUSE_STATE MOVE=…`, resume SD if paused). |
| `CANCEL_PRINT` | None in wrapper — clears `pending` and calls `_USER_CANCEL_PRINT`. |
| `GLOBAL_STATE`, `_SET_GLOBAL_STATE`, `STATE_REQUIRE`, `_PAUSE_PARK_STATE` introspection | None. |

### `filament.cfg`

| Macro | Motion |
|--------|--------|
| `_FILAMENT_LOAD_UNLOAD` | `M83`; load: `G1 E+LENGTH` then `G1 E+priming_length` at set speeds; unload: short forward `E`, pause `G4`, retract/shape oscillations, then long retract. May `ACTIVATE_EXTRUDER`. No XYZ. |
| `LOAD_FILAMENT` / `UNLOAD_FILAMENT` | Delegate to helper — **E only**. |
| `_FILAMENT_PAUSE_FOR_CHANGE` | If SD/host printing: `PAUSE` (see `state_guard`). Else if not paused and XYZ homed and idle lift is positive: `G91`, `G1 Z+idle_lift`, `G90`. |
| `M701` / `M702` | `_FILAMENT_PAUSE_FOR_CHANGE` then load/unload — **E** + optional **Z** lift as above. |
| `PAUSE_AFTER_D` / `PAUSE_AT_D` | When threshold reached: `PAUSE` (and optionally `UNLOAD_FILAMENT`). No extra motion in the delayed template itself beyond that. |

### `layers.cfg`

| Macro | Motion |
|--------|--------|
| `BEFORE_LAYER_CHANGE` / `AFTER_LAYER_CHANGE` / `_LAYER_RUN` | None — stats + runs **scheduled strings** (`COMMAND=…`), which may contain motion (e.g. `PAUSE`, `M220`). |
| `GCODE_AT_LAYER`, `PAUSE_NEXT_LAYER`, `PAUSE_AT_LAYER`, `SPEED_AT_LAYER`, `FLOW_AT_LAYER` | None at schedule time; motion when fired via `_LAYER_RUN`. |
| `INIT_LAYER_GCODE` / `RESET_LAYER_GCODE` / `CANCEL_ALL_LAYER_GCODE` | None. |

### `pid.cfg` — `PID_ALL`

No `G0`/`G1` in macro. Repeated `PID_CALIBRATE HEATER=…` — heater cycling and any probe motion are defined by Klipper’s PID implementation.

### `lock_accel.cfg`

`LOCK_ACCEL` / `UNLOCK_ACCEL` / overridden `SET_VELOCITY_LIMIT`: **no** tool moves (limits only).

### `lock_fan.cfg`

`LOCK_FAN` / `UNLOCK_FAN` / `M106` / `M107` / `SET_FAN_SPEED` overrides: **no** axis or extruder motion.

### `velocity.cfg`

**No** `G0`/`G1`. `M201` / `M203` / `M205` call `SET_VELOCITY_LIMIT` (ACCEL, VELOCITY, or SQUARE_CORNER_VELOCITY from Marlin-style X/Y min); bare call with no axis params forwards `SET_VELOCITY_LIMIT` alone. `M900` calls `SET_PRESSURE_ADVANCE` when `variable_pressure_advance_scale` > 0. `RESET_VELOCITY_LIMITS` sets `ACCEL` to `[printer] max_accel`.

### `optional/print_checkpoint.cfg`

| Macro / template | Motion |
|-------------------|--------|
| `_PRINT_CHECKPOINT_TICK`, `ENABLE_*` / `DISABLE_*` / `READ_*` | None (variables / `RESPOND` / `SAVE_VARIABLE`). |
| `RECOVER_PRINT_CHECKPOINT` | If `AUTO_SD=1`: virtual SD reset/load/seek (no steppers). Then `G28 X Y`, `G90`, `G1` to pause park XY, `M400`, `SET_KINEMATIC_POSITION X/Y/Z` (logical Z = saved Z + lift, `SET_HOMED=XYZ`). If `AUTO_SD=1`: `G1` to saved print XY, `G1` to saved Z; if `AUTO_SD=0`: skip those (handled by `RESUME`). Optional `M82` + `G92 E`. Heat only; then `M24` or `RESUME` per mode. |

### `optional/z_tilt_adjust.cfg` — `Z_TILT_ADJUST`

`SAVE_GCODE_STATE`; optional `BED_MESH_CLEAR`; conditional `_Z_TILT_ADJUST horizontal_move_z={lift} …` then `_Z_TILT_ADJUST`; `RESTORE_GCODE_STATE`. **XY/Z motion** is entirely inside stock / renamed `Z_TILT_ADJUST` (probing moves).

### `optional/quad_gantry_level.cfg` — `QUAD_GANTRY_LEVEL`

Same pattern as Z tilt: mesh clear, optional coarse `_QUAD_GANTRY_LEVEL` with `horizontal_move_z`, refinement pass, `RESTORE_GCODE_STATE`. **Motion** from stock QGL.

### `optional/test_speed.cfg` — `TEST_SPEED`

`SAVE_GCODE_STATE`; `M400`; `G28`; optional `QUAD_GANTRY_LEVEL` + `G28 Z`; `G90`; `G1` / `G0` positioning near max XY; `G28 X Y`; `G0` to near max corner; `G0` to `(x_min, y_min, Z=bound+10)` at test speed; raised `SET_VELOCITY_LIMIT`; many **`G0` box/diagonal patterns** inside build volume (large + small centre square); restore limits; `G28`; `G0` corner; `RESTORE_GCODE_STATE`.

### `optional/autotune_sgthrs.cfg` — `AUTOTUNE_SGTHRS_PHASE`

`SAVE_GCODE_STATE`; `G28`; `G0 Z{Z_SAFE}`; per SG value: `SET_VELOCITY_LIMIT`, square **`G0` pattern** around bed centre ±`RANGE`, diagonals, return centre; `G0` back to reference XY; **`G28 X Y`** for rehome check; loop; `RESTORE_GCODE_STATE`.

---

## Print checkpoint (`optional/print_checkpoint.cfg`)

Included from `globals.cfg`. Requires **`[save_variables]`** in `printer.cfg` (path to a writable variables file — see the comment header in `optional/print_checkpoint.cfg`).

**Bookmarking (during SD print)**

- `ENABLE_PRINT_CHECKPOINT` — starts periodic saves of pose + `virtual_sdcard` cursor (interval from `variable_checkpoint_interval` in `globals.cfg`, or `INTERVAL=` on the macro).
- `DISABLE_PRINT_CHECKPOINT` — stops the timer; `PRINT_END` also calls this.
- `READ_PRINT_CHECKPOINT` — prints last saved values to the console.

**Recovery — `RECOVER_PRINT_CHECKPOINT`**

Use after a fault when you still have a valid checkpoint on disk. **Wrong Z or file offset can damage the part or machine** — read the header in `optional/print_checkpoint.cfg`.

Default **`AUTO_SD=1`** (no separate Moonraker “resume job” step): `CLEAR_PAUSE`, `SDCARD_RESET_FILE`, **`M23`** + **`M26 S`** (byte offset from checkpoint), `G28 X Y`, pause park + `SET_KINEMATIC_POSITION` (logical Z = saved Z + `variable_pause_lift_z`), `G1` to saved print XYZ, heat, **`M24`**.

| Parameter | Meaning |
|-----------|---------|
| `AUTO_SD` | `1` (default): load file + offset and `M24`. `0`: only prep + `RESUME` if the job is already paused (e.g. Moonraker). |
| `FILENAME=` | Override path stored in variables (relative to `[virtual_sdcard]`). |
| `FILE_POS=` | Override byte offset (`print_ckpt_file_position`). |
| `BED=` / `EXTRUDER=` or `EXT=` | Heat targets (defaults: `variable_pid_*` in `globals.cfg`). |
| `LIFT=` | Pause lift (mm); default `variable_pause_lift_z`. |
| `SYNC_E=` | `1` (default): `M82` + `G92 E` from checkpoint; `0` to skip. |
| `SKIP_HEAT=1` | Do not wait on `M190` / `M109`. |
| `SKIP_RESUME=1` | With `AUTO_SD=1`: stop before `M24` (run `M24` yourself when ready). |

**Limitations**

- Stock Klipper **`M23` only lists files in the virtual SD root**; jobs in subfolders may fail to open unless you pass a workable `FILENAME=` or use a host script (e.g. `[gcode_shell_command]` + `RUN_SHELL_COMMAND` in a small wrapper macro — example in the checkpoint file header).
- Moonraker’s job panel may not match Klipper’s SD state after a raw `M24` recover; that is expected if you bypass the UI job queue.

---

## Command parameters and examples

### `PRINT_START`

- `BED`, `EXTRUDER` — targets (°C)
- `MESH_MIN`, `MESH_MAX` — mesh bounds (e.g. `30,30` / `200,200`)
- `LAYERS` — optional; runs `INIT_LAYER_GCODE` for `layers.cfg`

```gcode
PRINT_START BED=60 EXTRUDER=200 MESH_MIN=30,30 MESH_MAX=200,200
```

### `PRINT_END`

No parameters.

```gcode
PRINT_END
```

### `PAUSE_AFTER_D` (`filament.cfg`)

- `D` — extra extrusion (mm) from current `print_stats.filament_used` before pausing
- `AFTER` — `NONE` (default), `UNLOAD`, `REMIND`

```gcode
PAUSE_AFTER_D D=15
PAUSE_AFTER_D D=50 AFTER=UNLOAD
PAUSE_AFTER_D D=30 AFTER=REMIND
```

### Layer hooks (`layers.cfg`)

Slicer **Before / After layer change**:

```gcode
BEFORE_LAYER_CHANGE HEIGHT={layer_z} LAYER={layer_num}
AFTER_LAYER_CHANGE
```

Other scheduling (console / start G-code):

```gcode
GCODE_AT_LAYER LAYER=25 COMMAND="M117 layer 25"
PAUSE_NEXT_LAYER
SPEED_AT_LAYER LAYER=10 SPEED=80
```

Requires `[display_status]` so `SET_PRINT_STATS_INFO` exists.

### `PID_ALL`

Uses `variable_pid_ext_temp` and `variable_pid_bed_temp` from `globals.cfg`. Run **`SAVE_CONFIG`** after tuning.

```gcode
PID_ALL
```

### `LOCK_ACCEL` / `UNLOCK_ACCEL`

- `S` or `ACCEL` — enforced acceleration

```gcode
LOCK_ACCEL ACCEL=3000
UNLOCK_ACCEL
```

### `velocity.cfg` (`M201`, `M203`, `M205`, `M900`, `RESET_VELOCITY_LIMITS`)

- `M201 X=… Y=…` — `SET_VELOCITY_LIMIT ACCEL=min(X,Y)` (mm/s²). No X/Y: bare `SET_VELOCITY_LIMIT`.
- `M203 X=… Y=…` — `SET_VELOCITY_LIMIT VELOCITY=min(X,Y)` (mm/s).
- `M205 X=… Y=…` — `SET_VELOCITY_LIMIT SQUARE_CORNER_VELOCITY=min(X,Y)`.
- `M900 K=…` — `SET_PRESSURE_ADVANCE`; optional `T=` extruder index. Off if `variable_pressure_advance_scale` ≤ 0; else `ADVANCE = K * scale` (default scale `1.0` in `globals.cfg`).
- `RESET_VELOCITY_LIMITS` — `SET_VELOCITY_LIMIT ACCEL=<printer max_accel>`.

```gcode
M201 X3000 Y3000
M203 X150 Y150
M900 K0.04
RESET_VELOCITY_LIMITS
```

### `TEST_SPEED` *(optional include)*

`SPEED`, `ACCEL`, `ITERATIONS`, `BOUND`, `SMALLPATTERNSIZE`, `MIN_CRUISE_RATIO`

```gcode
TEST_SPEED SPEED=300 ACCEL=2500 ITERATIONS=4
```

### `Z_TILT_ADJUST` *(optional include)*

No parameters; one- or two-pass tilt per printer state.

### `QUAD_GANTRY_LEVEL` *(optional include)*

No parameters; QGL wrapper with lift/retry.

### `AUTOTUNE_SGTHRS_PHASE` *(optional include)*

`STEPPER`, `STEP`, `FEED`, `ACCEL`, `BOUND`, `SCALE_STEPS`, `MIN`, `MAX`

```gcode
AUTOTUNE_SGTHRS_PHASE STEPPER=stepper_x ACCEL=3000 FEED=240
```

---

## Installation

1. Copy the repo `.cfg` files into your Klipper config directory (or clone and point `[include]` at the folder).
2. In `printer.cfg`:

```ini
[include globals.cfg]
```

3. Add **`[save_variables]`** if you use print checkpoint (see `optional/print_checkpoint.cfg` header).
4. For other optional macros:

```ini
[include optional/test_speed.cfg]
[include optional/z_tilt_adjust.cfg]
```

(`print_checkpoint.cfg` is already included via `globals.cfg`; disable by editing `globals.cfg` if you do not want it.)

---

## Slicer G-code (PrusaSlicer-style example)

### Start

```gcode
PRINT_START BED=[first_layer_bed_temperature] EXTRUDER=[first_layer_temperature] \
  MESH_MIN=[first_layer_print_min[0]],[first_layer_print_min[1]] \
  MESH_MAX=[first_layer_print_max[0]],[first_layer_print_max[1]]
```

### End

```gcode
PRINT_END
```

---

## Highlights

- Global tuning via `_macro_globals` in `globals.cfg`
- Pause/park/restore coordinated with `PAUSE` / `RESUME` in `state_guard.cfg`
- Filament load/unload and distance-based pause (`PAUSE_AFTER_D`)
- Layer-change automation (`layers.cfg`)
- Optional SD checkpoint + recover path (`print_checkpoint.cfg`)
- Marlin-style limits / PA via `velocity.cfg` (`M201`, `M203`, `M205`, `M900`)
- `RESPOND` messages for operator feedback

---

## Formatting (development)

- **Editor:** open the repo folder in Cursor/VS Code — workspace settings trim trailing whitespace, insert a final newline, and use LF on save (see `.vscode/settings.json`). `.editorconfig` aligns other editors (install the EditorConfig extension if needed).
- **CLI (whole tree):** from repo root run `python scripts/format_all.py` to normalize `.cfg`, `.md`, `.mdc`, `.ini`, `.json`, `.yml`/`.yaml` under the tree (skips `.git`, etc.).
- **Contributors / agents:** follow `.cursor/rules/format-before-save.mdc` when changing tracked text files.

---

## License

MIT — use, modify, and share freely.
