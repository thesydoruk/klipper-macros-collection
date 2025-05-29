# 🧩 Klipper Macro Suite

A clean, modular, and hardware-agnostic collection of macros for [Klipper](https://www.klipper3d.org/) firmware.
Each macro is designed for performance, print safety, configurability, and ease of maintenance.

---

## 📦 Included Macros

### 🛫 `PRINT_START`
Smart print initialization with automatic heating, homing, optional Z-tilt correction, mesh leveling, and purge line generation.

### 🛬 `PRINT_END`
Safely finalizes prints: retracts filament, lifts Z, parks the toolhead, disables heaters, and resets modifiers.

### ⏸️ `PAUSE_AFTER_D`
Delays a print pause until an additional `D` mm of filament is extruded — useful for color swaps or user intervention.

### 🔥 `PID_B`, `PID_E`
Macros for autotuning the heated bed and hotend. Safe input ranges and defaults are enforced via global config.

### 🚫 `LOCK_ACCEL`, `UNLOCK_ACCEL`, `M204`, `SET_VELOCITY_LIMIT`
Accurate locking of acceleration values mid-print. Prevents G-code from altering acceleration unintentionally.

### 🧪 `TEST_SPEED`
Run high-speed movement tests across defined toolhead patterns to detect motion inconsistencies or skipped steps.

### ⚖️ `Z_TILT_ADJUST`
Two-phase safe tilt alignment with configurable lift height. Automatically skips high-pass if tilt is already applied.

### 🪜 `QUAD_GANTRY_LEVEL`
Enhanced QGL macro that lifts the gantry before leveling and restores motion state after.

### 🧠 `AUTOTUNE_SGTHRS_PHASE`
Auto-detects ideal StallGuard threshold by scanning SG_RESULT across multiple load profiles. Provides recommended config line.

### ⚙️ `_macro_globals`
Centralized macro config block. Defines all configurable variables for purge, lift, limits, tolerances, and more.
**This macro is required and must be included.**

---

## 🛠️ Setup Instructions

1. Copy all `.cfg` files to your Klipper config folder (typically on your Pi or MCU host).
2. Include the required macros in your `printer.cfg`:

```ini
[include globals.cfg]              # REQUIRED
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

3. Configure your slicer (example for **PrusaSlicer**):

### Start G-code:
```gcode
M190 S[first_layer_bed_temperature]
M104 S[first_layer_temperature]
START_PRINT BED=[first_layer_bed_temperature] EXTRUDER=[first_layer_temperature] \
  MESH_MIN=[first_layer_print_min[0]],[first_layer_print_min[1]] \
  MESH_MAX=[first_layer_print_max[0]],[first_layer_print_max[1]]
```

### End G-code:
```gcode
END_PRINT
```

---

## 💡 Design Principles

- 📁 **Separation of Logic** — All logic lives in macros, not in slicers.
- 🧰 **Configurability** — All parameters are sourced from `_macro_globals`.
- 🧱 **Recoverable & Safe** — Motion states are saved/restored. Meshes are cleared when needed.
- 🖥️ **Clear Feedback** — Uses `RESPOND` messages to provide user-readable logging.
- 🔀 **Hardware-Agnostic** — Works across Vorons, bedslingers, CoreXY, and other setups.

---

## 📄 License

MIT License. Free to use, share, and adapt.

---
