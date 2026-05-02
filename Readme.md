# Klipper Macro Collection

This repository is a small, practical macro set for Klipper printers. It tries to keep slicer start/end G-code simple, put printer behavior in one place, and make pause, resume, filament changes, layer actions, velocity limits, and optional print checkpoints easier to reason about.

Ukrainian docs: [Readme.uk.md](Readme.uk.md)

## What You Get

Include `globals.cfg` once from `printer.cfg`. It pulls in the core macro files and exposes shared settings through `_macro_globals`.

```ini
[include globals.cfg]
```

Core files loaded by `globals.cfg`:

- `print_start.cfg`: `PRINT_START` for heating, homing, tilt/QGL, mesh, and purge.
- `print_end.cfg`: `PRINT_END` for retract, lift, park, cooldown, and cleanup.
- `state_guard.cfg`: wraps `PRINT_START`, `PRINT_END`, `PAUSE`, `RESUME`, and `CANCEL_PRINT`; tracks `GLOBAL_STATE`; restores the parked toolhead after pause.
- `filament.cfg`: `LOAD_FILAMENT`, `UNLOAD_FILAMENT`, `M701`, `M702`, and `PAUSE_AFTER_D`.
- `layers.cfg`: slicer layer hooks and scheduled commands such as `PAUSE_AT_LAYER`, `SPEED_AT_LAYER`, and `FLOW_AT_LAYER`.
- `pid.cfg`: `PID_ALL` for bed and configured extruders.
- `lock_accel.cfg`: `LOCK_ACCEL` / `UNLOCK_ACCEL` with a protected `SET_VELOCITY_LIMIT`.
- `lock_fan.cfg`: `LOCK_FAN` / `UNLOCK_FAN` with protected fan commands.
- `velocity.cfg`: Marlin-style `M201`, `M203`, `M205`, `M900`, and `RESET_VELOCITY_LIMITS`.
- `optional/print_checkpoint.cfg`: included by default; periodically saves SD print position and can prepare a recovery attempt.

Optional files you include only when you need them:

```ini
[include optional/test_speed.cfg]
[include optional/z_tilt_adjust.cfg]
[include optional/quad_gantry_level.cfg]
[include optional/autotune_sgthrs.cfg]
```

## Install

1. Copy or clone this repository into your Klipper config area.
2. Add this to `printer.cfg`:

```ini
[include globals.cfg]
```

3. If you want print checkpoints, add `[save_variables]` to `printer.cfg`. The required shape is shown in the header of `optional/print_checkpoint.cfg`.
4. Restart Klipper and check the console for missing dependencies.

If you do not want checkpoint macros at all, comment out this line in `globals.cfg`:

```ini
[include optional/print_checkpoint.cfg]
```

## Slicer Setup

The slicer should call the printer-level macros. Do not duplicate full homing, bed mesh, and long heat waits in slicer start G-code if `PRINT_START` already does that work.

### PrusaSlicer, SuperSlicer, OrcaSlicer

Start G-code:

```gcode
PRINT_START BED=[first_layer_bed_temperature] EXTRUDER=[first_layer_temperature] \
  MESH_MIN=[first_layer_print_min[0]],[first_layer_print_min[1]] \
  MESH_MAX=[first_layer_print_max[0]],[first_layer_print_max[1]]
```

If your slicer has a reliable total-layer placeholder, pass it too:

```gcode
PRINT_START BED=[first_layer_bed_temperature] EXTRUDER=[first_layer_temperature] \
  MESH_MIN=[first_layer_print_min[0]],[first_layer_print_min[1]] \
  MESH_MAX=[first_layer_print_max[0]],[first_layer_print_max[1]] \
  LAYERS=[total_layer_count]
```

If your slicer does not expose total layers, leave `LAYERS=` out. Height-based scheduled commands still work.

End G-code:

```gcode
PRINT_END
```

Before layer change:

```gcode
BEFORE_LAYER_CHANGE HEIGHT={layer_z} LAYER={layer_num}
```

After layer change:

```gcode
AFTER_LAYER_CHANGE
```

Layer hooks need `[display_status]` in `printer.cfg`, because the macros use `SET_PRINT_STATS_INFO`.

### Cura

Cura placeholders are different. A simple start example:

```gcode
PRINT_START BED={material_bed_temperature_layer_0} EXTRUDER={material_print_temperature_layer_0} MESH_MIN=30,30 MESH_MAX=200,200
```

Set `MESH_MIN` / `MESH_MAX` to match your printable bed area, or omit them if you want `PRINT_START` to skip adaptive mesh bounds.

End G-code:

```gcode
PRINT_END
```

Cura does not have the same simple before/after layer hooks as Prusa-family slicers. If you rely on `layers.cfg`, use Cura post-processing / insert-at-layer tooling to inject `BEFORE_LAYER_CHANGE` and `AFTER_LAYER_CHANGE`.

### Pressure Advance, Velocity, and Filament Change

If your slicer emits `M201`, `M203`, or `M205`, `velocity.cfg` maps those to Klipper `SET_VELOCITY_LIMIT`. Acceleration changes still pass through `lock_accel.cfg`.

`M900 K=...` maps to `SET_PRESSURE_ADVANCE` when `variable_pressure_advance_scale` in `globals.cfg` is greater than zero. Set it to `0` if you want to ignore slicer `M900` and manage pressure advance elsewhere.

This collection does not define `M600` by default. For slicer filament-change G-code, use `PAUSE`, or add your own `M600` macro that calls `PAUSE` and any filament workflow you want.

## Common Commands

`PRINT_START` is the normal entry point from the slicer. It expects at least `BED` and `EXTRUDER`; `MESH_MIN` and `MESH_MAX` are recommended when the slicer can provide the first-layer area.

```gcode
PRINT_START BED=60 EXTRUDER=200 MESH_MIN=30,30 MESH_MAX=200,200
```

`PRINT_END` has no parameters:

```gcode
PRINT_END
```

Filament helpers:

```gcode
LOAD_FILAMENT
UNLOAD_FILAMENT
M701 L=80
M702 U=80
```

Pause after a certain amount of filament has been used:

```gcode
PAUSE_AFTER_D D=15
PAUSE_AFTER_D D=50 AFTER=UNLOAD
PAUSE_AFTER_D D=30 AFTER=REMIND
```

Layer scheduling:

```gcode
GCODE_AT_LAYER LAYER=25 COMMAND="M117 layer 25"
PAUSE_NEXT_LAYER
SPEED_AT_LAYER LAYER=10 SPEED=80
FLOW_AT_LAYER LAYER=20 FLOW=95
```

PID tune all configured heaters:

```gcode
PID_ALL
SAVE_CONFIG
```

Acceleration and fan locks:

```gcode
LOCK_ACCEL ACCEL=3000
UNLOCK_ACCEL

LOCK_FAN SPEED=0.5
UNLOCK_FAN
```

Marlin-style velocity / pressure advance compatibility:

```gcode
M201 X3000 Y3000
M203 X150 Y150
M205 X5 Y5
M900 K0.04
RESET_VELOCITY_LIMITS
```

Optional diagnostics:

```gcode
TEST_SPEED SPEED=300 ACCEL=2500 ITERATIONS=4
AUTOTUNE_SGTHRS_PHASE STEPPER=stepper_x ACCEL=3000 FEED=240
```

## Print Checkpoints and Recovery

`optional/print_checkpoint.cfg` is included from `globals.cfg`. It is meant for Moonraker / Mainsail-style `[virtual_sdcard]` printing, not raw USB streaming from a slicer.

Required config:

```ini
[save_variables]
filename: ~/printer_data/config/print_checkpoint_vars.cfg
```

Start periodic bookmarking:

```gcode
ENABLE_PRINT_CHECKPOINT
```

Optional interval override:

```gcode
ENABLE_PRINT_CHECKPOINT INTERVAL=10
```

Read the last saved checkpoint:

```gcode
READ_PRINT_CHECKPOINT
```

Stop bookmarking:

```gcode
DISABLE_PRINT_CHECKPOINT
```

Recovery is intentionally conservative. `RECOVER_PRINT_CHECKPOINT` can load the saved file and byte offset through virtual SD (`AUTO_SD=1`), home XY, place the toolhead in the same logical state as a paused print, heat, and start with `M24`.

```gcode
RECOVER_PRINT_CHECKPOINT
```

Useful recovery parameters:

- `AUTO_SD=1`: default; load file with `M23`, seek with `M26`, and start with `M24`.
- `AUTO_SD=0`: prepare the position, then use `RESUME` only if the job is already paused.
- `FILENAME=` and `FILE_POS=`: override saved values.
- `BED=` / `EXTRUDER=` or `EXT=`: override heat targets.
- `LIFT=`: override the pause lift used when setting logical Z.
- `SYNC_E=0`: skip `G92 E...`.
- `SKIP_HEAT=1`: do not wait on heaters.
- `SKIP_RESUME=1`: stop before `M24` / `RESUME`.

Be careful: a wrong Z position, wrong byte offset, or moved part can crash the nozzle into the print. Stock Klipper `M23` may also fail on files in subfolders; use `FILENAME=` or a host-side script wrapper if needed.

## Kinematics Reference

This section is deliberately explicit. Any future macro change that changes toolhead motion should update it. See `.cursor/rules/gcode-kinematics-doc.mdc`.

Conventions: `G90` means absolute coordinates, `G91` means relative coordinates, and `E` means extruder-only movement. When a macro delegates to a Klipper built-in such as `BED_MESH_CALIBRATE`, `Z_TILT_ADJUST`, or `PID_CALIBRATE`, the exact path comes from your printer config and Klipper itself.

### `globals.cfg`

No motion. It only includes files and stores variables.

### `print_start.cfg`

`PRINT_START` sets `G90` and `M83`, then performs a full `G28`. If mesh bounds are provided, it either runs the eddy path (`G1 Z10 F900`, move to mesh center at `F6000`, `PROBE_EDDY_NG_TAP`, `EDDYNG_BED_MESH_EXPERIMENTAL`) or calls `BED_MESH_CALIBRATE` with the configured mesh arguments.

The purge section resets E with `G92 E0`, moves to `Z2` at `F900`, travels to the purge start at `F6000`, lowers to the purge height at `F300`, primes with `G1 E... F300`, then draws alternating purge lines with X/Y/E movement at the configured purge feedrate. It ends with `G92 E0`.

`INIT_LAYER_GCODE`, when called through `LAYERS=`, does not move the toolhead.

### `print_end.cfg`

If XYZ is homed, `PRINT_END` switches to `G91`, retracts `E` at `F1800`, lifts Z at `F900`, switches back to `G90`, then parks at configured X/Y with `F6000`.

If axes are not homed, it skips retract, lift, and park and only restores `G90`. Cooldown, mesh clear, fan off, flow/speed reset, layer reset, checkpoint disable, and eddy tap reset do not move XYZ or E.

### `state_guard.cfg`

The `PRINT_START` and `PRINT_END` wrappers only update state and forward to the real macros.

`PAUSE` saves the current position. After stock pause and `M400`, if XYZ is homed and pause lift is positive, it runs `G91`, lifts Z by `variable_pause_lift_z` at `variable_pause_lift_feedrate`, returns to `G90`, then moves to configured park X/Y at `variable_pause_park_feedrate`.

`RESUME` returns from the pause park if `_PAUSE_PARK_STATE.pending` is set: `G90`, move to saved X/Y, then move to saved Z. It then clears `pending` and calls the renamed stock resume.

`CANCEL_PRINT`, `GLOBAL_STATE`, `_SET_GLOBAL_STATE`, `STATE_REQUIRE`, and `_PAUSE_PARK_STATE` introspection do not add motion.

### `filament.cfg`

`LOAD_FILAMENT` and `UNLOAD_FILAMENT` delegate to `_FILAMENT_LOAD_UNLOAD`. That helper uses `M83` and moves only E. Load pushes `LENGTH`, then `priming_length`. Unload does a small forward move, a dwell, shaping oscillations, and a longer retract.

`M701` and `M702` first run `_FILAMENT_PAUSE_FOR_CHANGE`. During a print that means `PAUSE`. While idle, if the printer is homed and idle lift is enabled, it does `G91`, a Z lift, and `G90`. Then it performs the load or unload E moves.

`PAUSE_AFTER_D` only monitors filament usage. When it fires, it calls `PAUSE` and optionally `UNLOAD_FILAMENT` or reminder beeps.

### `layers.cfg`

Layer macros do not move by themselves. They update print stats and run scheduled command strings. If you schedule `PAUSE`, `M220`, or any `G1`, that scheduled command is responsible for motion.

### `pid.cfg`

`PID_ALL` does not issue `G0` or `G1`. It calls `PID_CALIBRATE` for the configured extruders and bed.

### `lock_accel.cfg`, `lock_fan.cfg`, `velocity.cfg`

These macros do not move the toolhead. They change limits, fan state, or pressure advance. `velocity.cfg` maps `M201`, `M203`, `M205`, and `M900` to Klipper limit / pressure advance commands.

### `optional/print_checkpoint.cfg`

Bookmarking macros only read status and save variables.

`RECOVER_PRINT_CHECKPOINT` with `AUTO_SD=1` resets/selects/seeks virtual SD without stepper motion, then runs `G28 X Y`, `G90`, moves to pause park X/Y, waits with `M400`, and uses `SET_KINEMATIC_POSITION X=... Y=... Z=... SET_HOMED=XYZ` where logical Z is saved print Z plus pause lift. It then moves to saved print X/Y, moves down to saved Z, optionally runs `M82` and `G92 E...`, heats, and starts with `M24`.

With `AUTO_SD=0`, it prepares the same logical paused state but leaves the final return to `RESUME`.

### Optional leveling and diagnostics

`optional/z_tilt_adjust.cfg` wraps the stock `Z_TILT_ADJUST`: save state, clear mesh if present, optional coarse pass with `horizontal_move_z`, final pass, restore state. Motion is the stock Klipper Z tilt probe path.

`optional/quad_gantry_level.cfg` does the same for `QUAD_GANTRY_LEVEL`: optional coarse pass, final pass, restore state. Motion is the stock QGL path.

`optional/test_speed.cfg` homes with `G28`, optionally runs QGL and `G28 Z`, switches to `G90`, moves near max XY, homes XY, moves to a near-corner reference, raises to `Z=bound+10`, applies velocity limits, runs repeated large and small `G0` box/diagonal patterns, restores limits, homes again, returns to a corner, and restores G-code state.

`optional/autotune_sgthrs.cfg` saves state, runs `G28`, moves to `Z_SAFE`, then for each SG value runs a square and diagonal `G0` pattern around bed center, returns to the reference point, runs `G28 X Y`, checks drift, and restores state at the end.

## Development Notes

Before finishing edits to `.cfg`, `.md`, `.mdc`, `.ini`, JSON, or YAML files, run:

```shell
python scripts/format_all.py
```

The repo also contains `.editorconfig`, `.gitattributes`, and workspace settings for LF line endings, final newlines, and trimmed trailing whitespace.

## License

MIT. Use it, change it, and adapt it to your printer.
