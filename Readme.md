# 📘 Klipper Macro Collection

A modular set of well-documented Klipper macros designed to improve reliability, maintainability, and configurability of your 3D printer setup.

---

## 📁 Macros Overview

Below is an overview of included files and the G-code commands they provide.

### `globals.cfg`
Contains all configurable variables used across macros — heater targets, purge behavior, acceleration limits, autotune thresholds, etc. This file **must be included** in your Klipper config.
It also includes the core macros listed below:

### Included by `globals.cfg`
These macros are included automatically when you load `globals.cfg`:

- **`print_start.cfg`** — Defines `PRINT_START` for full pre-print setup.
- **`print_end.cfg`** — Provides `PRINT_END` to safely finish a print.
- **`filament.cfg`** — Public surface like imported km: `LOAD_FILAMENT`, `UNLOAD_FILAMENT`, `M701`, `M702`; plus `PAUSE_AFTER_D` (`AFTER=UNLOAD|REMIND`). Underscore-prefixed names in sources are internal helpers only.
- **`layers.cfg`** — `BEFORE_LAYER_CHANGE` / `AFTER_LAYER_CHANGE` (slicer hooks), `GCODE_AT_LAYER`, `INIT_LAYER_GCODE` (optional `LAYERS` in `PRINT_START`), `RESET_LAYER_GCODE` (from `PRINT_END`), `CANCEL_ALL_LAYER_GCODE`, `PAUSE_NEXT_LAYER`, `PAUSE_AT_LAYER`, `SPEED_AT_LAYER`, `FLOW_AT_LAYER`. Needs `[display_status]` for `SET_PRINT_STATS_INFO` / `print_stats.info`. Internal: `_LAYER_RUN`.
- **`pid.cfg`** — Adds `PID_B` and `PID_E` to autotune bed and hotend.
- **`lock_accel.cfg`** — Implements `LOCK_ACCEL`, `UNLOCK_ACCEL`, and overrides `M204` and `SET_VELOCITY_LIMIT` to block changes.

### Optional Macros (include manually if needed) (include manually if needed)
These macros are stored in the `optional/` folder and must be explicitly included:

- **`z_tilt_adjust.cfg`** — Provides the `Z_TILT_ADJUST` command for safe 2-pass alignment.
- **`quad_gantry_level.cfg`** — Defines `QUAD_GANTRY_LEVEL` macro that handles lifting, retrying, and state restore.
- **`test_speed.cfg`** — Adds `TEST_SPEED`, which runs high-speed motion diagnostics with delta detection.
- **`autotune_sgthrs.cfg`** — Adds `AUTOTUNE_SGTHRS_PHASE`, which finds optimal sensorless SGTHRS value.

---

## 🧪 Command Parameters & Usage Examples

### `PRINT_START`
**Parameters:**
- `BED` — target bed temperature (°C)
- `EXTRUDER` — target hotend temperature (°C)
- `MESH_MIN` — lower-left corner of mesh probe area (e.g. `30,30`)
- `MESH_MAX` — upper-right corner of mesh probe area (e.g. `200,200`)
- `LAYERS` — optional; if set, runs `INIT_LAYER_GCODE` for `layers.cfg` (slicer layer count / Prusa-style)

**Example:**
```gcode
START_PRINT BED=60 EXTRUDER=200 MESH_MIN=30,30 MESH_MAX=200,200
```

### `PRINT_END`
**No parameters.** Cleans up after printing.
```gcode
END_PRINT
```

### `PAUSE_AFTER_D`
**Parameters:**
- `D` — additional extrusion (mm) from current `print_stats.filament_used` before pausing
- `AFTER` — optional: `NONE` (default), `UNLOAD` (run `UNLOAD_FILAMENT` after `PAUSE`), `REMIND` (`M117` + beeps)

**Examples:**
```gcode
PAUSE_AFTER_D D=15
PAUSE_AFTER_D D=50 AFTER=UNLOAD
PAUSE_AFTER_D D=30 AFTER=REMIND
```

### Layer hooks (`layers.cfg`)
Put in the slicer **Before layer change** / **After layer change** custom G-code:
```gcode
BEFORE_LAYER_CHANGE HEIGHT={layer_z} LAYER={layer_num}
AFTER_LAYER_CHANGE
```
Schedule once (e.g. from console or start G-code):
```gcode
GCODE_AT_LAYER LAYER=25 COMMAND="M117 layer 25"
PAUSE_NEXT_LAYER
SPEED_AT_LAYER LAYER=10 SPEED=80
```
Requires `[display_status]` (or equivalent) so `SET_PRINT_STATS_INFO` exists.

### `PID_B`, `PID_E`
**Parameters:**
- `T` — optional target temp for PID tuning (°C)

**Examples:**
```gcode
PID_B T=70      ; tune bed to 70°C
PID_E           ; tune hotend to default temp
```

### `LOCK_ACCEL`, `UNLOCK_ACCEL`
**LOCK_ACCEL Parameters:**
- `S` or `ACCEL` — acceleration value to enforce

**Examples:**
```gcode
LOCK_ACCEL ACCEL=3000
UNLOCK_ACCEL
```

### `TEST_SPEED` *(optional)*
**Parameters:**
- `SPEED`, `ACCEL`, `ITERATIONS`, `BOUND`, `SMALLPATTERNSIZE`, `MIN_CRUISE_RATIO`

**Example:**
```gcode
TEST_SPEED SPEED=300 ACCEL=2500 ITERATIONS=4
```

### `Z_TILT_ADJUST` *(optional)*
**No parameters.** Runs 1 or 2 passes of tilt leveling depending on current printer state.

### `QUAD_GANTRY_LEVEL` *(optional)*
**No parameters.** Wrapper for QGL with extra lift and retry.

### `AUTOTUNE_SGTHRS_PHASE` *(optional)*
**Parameters:**
- `STEPPER`, `STEP`, `FEED`, `ACCEL`, `BOUND`, `SCALE_STEPS`, `MIN`, `MAX`

**Example:**
```gcode
AUTOTUNE_SGTHRS_PHASE STEPPER=stepper_x ACCEL=3000 FEED=240
```

---

## 🧰 Installation

1. Copy all `.cfg` files into your Klipper config directory
2. In `printer.cfg`, include this line:

```ini
[include globals.cfg]  # includes all core macros
```

3. To enable optional macros, add them manually:
```ini
[include optional/test_speed.cfg]
[include optional/z_tilt_adjust.cfg]
```

---

## 🖨️ Slicer G-code (PrusaSlicer example)

### Start G-code
```gcode
START_PRINT BED=[first_layer_bed_temperature] EXTRUDER=[first_layer_temperature] \
  MESH_MIN=[first_layer_print_min[0]],[first_layer_print_min[1]] \
  MESH_MAX=[first_layer_print_max[0]],[first_layer_print_max[1]]
```

### End G-code
```gcode
END_PRINT
```

---

## ✅ Highlights

- 🔒 Acceleration lock for consistent motion
- 🔁 Automatic mesh and tilt routines
- 🧪 Built-in test patterns for motion tuning
- 📊 Detailed console feedback via RESPOND
- ⚙️ Globalized config for easy tuning
- 💡 Minimal slicer logic: macros handle everything

---

## 📝 License

MIT — use, modify, and share freely.
