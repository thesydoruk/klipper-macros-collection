# Klipper Macros Collection

A curated and production-tested collection of adaptive, documented, and highly modular macros for Klipper. This repository provides drop-in replacements and extensions for common printer workflows — including reliable `PRINT_START`, `PRINT_END`, Z tilt, mesh leveling, probe support, pause triggers, and system calibration.

> ⚡ Designed for real-world robustness, edge-case safety, and compatibility with forks like **Kalico** and probes like **Eddy / probe_eddy_ng**.

---

## ✨ Features

- ✅ Adaptive `PRINT_START`:
  - Kalico support (`ADAPTIVE=1`)
  - `probe_eddy_ng` → `EDDYNG_BED_MESH_EXPERIMENTAL`
  - `probe_eddy_*` → `METHOD=rapid_scan`
  - dynamic purge lines in front of mesh area
- ✅ Clean `PRINT_END`:
  - configurable retract, lift, and park
  - disables heaters and fans
  - resets mesh, speed (M220), flow (M221)
  - clears `probe_eddy_ng` tap offset
- ✅ Smart `Z_TILT_ADJUST` and `QUAD_GANTRY_LEVEL`:
  - uses enhanced flow for Eddy systems
  - defaults to stock commands otherwise
  - coarse pass height is user-configurable
- ✅ Extrusion-aware pause trigger: `PAUSE_AFTER_D`
- ✅ PID tuning macros: `PID_E`, `PID_B`
- ✅ Motion test utility: `TEST_SPEED` with MCU step validation

---

## 📁 Configuration via `_print_settings`

Macros are centrally configured using:

```ini
[gcode_macro _print_settings]

# Purge control
variable_start_purge_length: 30.0
variable_start_purge_prime_length: 5.0
variable_start_purge_offset_y: 5.0
variable_start_purge_feedrate: 1200.0

# Heating behavior
variable_start_extruder_preheat_scale: 0.5
variable_start_bed_heat_overshoot: 2.0
variable_start_bed_heat_delay: 2.0

# End-of-print
variable_end_retract_length: 2.0
variable_end_lift_z: 10.0
variable_end_park_x: min
variable_end_park_y: max

# Z tilt / QGL behavior
variable_z_tilt_lift: 8.0
variable_qgl_lift: 8.0

gcode:
```

You only need to configure this once. All macros reference these values dynamically.

---

## 🧩 Slicer Integration

The `PRINT_START` macro requires the following parameters from your slicer:

- `BED` – target bed temperature (°C)
- `EXTRUDER` – target nozzle temperature (°C)
- `MESH_MIN` – mesh area bottom-left point as `X,Y`
- `MESH_MAX` – mesh area top-right point as `X,Y`

### ✅ Example for PrusaSlicer / SuperSlicer:

```gcode
PRINT_START BED={first_layer_bed_temperature} EXTRUDER={first_layer_temperature} MESH_MIN={min_print_x},{min_print_y} MESH_MAX={max_print_x},{max_print_y}
```

> Ensure the slicer resolves these placeholders at export.

---

## 🔚 PRINT_END

`PRINT_END` performs a clean shutdown sequence:

- Retracts and lifts the nozzle
- Parks toolhead in configurable position (`X min`, `Y max` by default)
- Turns off all heaters and fans
- Clears:
  - Bed mesh (`BED_MESH_CLEAR`)
  - Speed factor (M220)
  - Flow factor (M221)
- Resets `probe_eddy_ng` tap offset:
  ```gcode
  PROBE_EDDY_NG_SET_TAP_OFFSET VALUE=0
  ```

Configuration is fully handled via `_print_settings`.

---

## 🧠 Smart Adaptation

Macros automatically detect and adapt to:

- Kalico fork support via command template analysis
- `probe_eddy_*` and `probe_eddy_ng` sections
- Whether `z_tilt` or `quad_gantry_level` are configured
- Whether a coarse pass is needed before fine adjustment

No manual flags or edits are needed.

---

## 📜 License

This project is released under the [MIT License](LICENSE). You are free to use, modify, and distribute.

---

## 🙏 Credits

Inspired by:
- [jschuh/klipper-macros](https://github.com/jschuh/klipper-macros)
- [AndrewEllis93/Print-Tuning-Guide](https://github.com/AndrewEllis93/Print-Tuning-Guide)

Extended, tested, and maintained by [@thesydoruk](https://github.com/thesydoruk)
