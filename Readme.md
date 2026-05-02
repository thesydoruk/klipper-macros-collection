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
| `lock_accel.cfg` | `LOCK_ACCEL` / `UNLOCK_ACCEL`; overrides `M204` / `SET_VELOCITY_LIMIT`. |
| `lock_fan.cfg` | Protects a chosen fan from slicer overrides. |
| `optional/print_checkpoint.cfg` | SD bookmarks + optional recovery (see below). |

### Optional files (include yourself)

These live under `optional/` and are **not** pulled in by `globals.cfg` unless you add another `[include …]`:

- `optional/z_tilt_adjust.cfg` — `Z_TILT_ADJUST`
- `optional/quad_gantry_level.cfg` — `QUAD_GANTRY_LEVEL`
- `optional/test_speed.cfg` — `TEST_SPEED`
- `optional/autotune_sgthrs.cfg` — `AUTOTUNE_SGTHRS_PHASE`

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
- `RESPOND` messages for operator feedback

---

## License

MIT — use, modify, and share freely.
