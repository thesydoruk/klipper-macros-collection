# 📘 Klipper Macro Collection

A modular set of well-documented Klipper macros designed to improve reliability, maintainability, and configurability of your 3D printer setup.

---

## 📁 Macros Overview

### `globals.cfg`
Contains all configurable variables used across macros — heater targets, purge behavior, acceleration limits, autotune thresholds, etc. This file **must be included** in your Klipper config.

### `print_start.cfg`
Performs full startup: heating, homing, optional gantry leveling, mesh calibration, and purge lines. Supports smart preheat staging and adaptive purge parameters.

### `print_end.cfg`
Cleans up after printing by retracting, lifting the nozzle, parking, and disabling heaters. Mesh and motion parameters are reset.

### `pause_after_d.cfg`
Pauses the printer after a configurable amount of filament is consumed. Useful for controlled swaps or interventions.

### `pid.cfg`
Macros `PID_B` and `PID_E` for autotuning bed and hotend heaters with optional temperature validation. Uses values from `globals.cfg`.

### `lock_accel.cfg`
Implements a mechanism to lock acceleration settings during print. Prevents G-code from overriding acceleration via `M204` or `SET_VELOCITY_LIMIT`.

### `test_speed.cfg`
Executes aggressive motion patterns to test axis reliability. Supports configurable speeds, bounds, and pattern scaling. Includes position delta checks to detect skips.

### `quad_gantry_level.cfg`
Wrapper around QGL with automatic lift and recovery. Supports skipped first pass if already applied.

### `z_tilt_adjust.cfg`
Safe Z tilt leveling with conditional high-pass and restoration of printer state.

### `autotune_sgthrs.cfg`
StallGuard SGTHRS autotuning for sensorless homing. Performs motion stress tests and recommends a threshold value with position delta analysis.

---

## 🧰 Installation

1. Copy all `.cfg` files to your Klipper config folder
2. In your `printer.cfg`, include:

```ini
[include globals.cfg]  # required
[include print_start.cfg]
[include print_end.cfg]
[include pause_after_d.cfg]
[include pid.cfg]
[include lock_accel.cfg]
[include test_speed.cfg]
[include z_tilt_adjust.cfg]
[include quad_gantry_level.cfg]
[include autotune_sgthrs.cfg]
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

- Designed for real-world use (Voron, bedslingers, CoreXY, delta)
- Parameterized with `_macro_globals`
- Safe, fail-resistant behavior with clean G-code state management
- Human-readable console output using `RESPOND`
- Minimal assumptions about hardware

---

## 📝 License

MIT — use, modify, and share freely.
