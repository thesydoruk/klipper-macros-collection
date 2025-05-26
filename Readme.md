# 🧩 Klipper Macro Suite

This repository contains a set of powerful and modular macros for [Klipper](https://www.klipper3d.org/) firmware. They are designed to improve print start/end procedures, motion reliability, probing accuracy, and general control safety.

Each macro is fully documented and structured to be hardware-agnostic, extensible, and compatible with Kalico/Eddy/Fluidd/Mainsail.

---

## 📂 Macro Files Overview

### `print_start.cfg`
Smart and adaptive `PRINT_START` macro:
- Supports Kalico/Eddy/NG probes and dynamic toolhead types
- Automatically purges filament based on tool type and nozzle location
- Synchronizes heating between bed/nozzle for efficiency
- Logs each step with RESPOND messages (`TYPE=echo`)
- Designed to replace slicer G-code completely

### `print_end.cfg`
Comprehensive `PRINT_END` macro:
- Retracts filament
- Disables heaters/fans safely
- Parks the toolhead and lifts Z
- Fully configurable and tool-agnostic
- Complements `PRINT_START`

### `pause_after_d.cfg`
Macro that watches for G1 moves containing a `D` parameter and pauses the print after such moves. Useful for:
- Manual insertions
- Print inspection
- Custom pause triggers

### `print_settings.cfg`
Centralized macro configuration:
- Defines shared variables (e.g. purge lengths, retract amounts, wipe settings)
- Used across macros via `SET_GCODE_VARIABLE`
- Enables macros to behave consistently regardless of slicer

> ⚠️ **Note**: This is *not* for slicer-generated settings — it’s for internal macro parameterization.

### `pid.cfg`
Macros for PID autotuning:
- Simplifies tuning heater PID values
- Provides clear user feedback
- Logs and restores settings

### `lock_accel.cfg`
Implements an acceleration lock mechanism:
- Prevents macros and G-code from modifying acceleration mid-print
- Includes:
  - `LOCK_ACCEL`
  - `UNLOCK_ACCEL`
  - Patched `M204` and `SET_VELOCITY_LIMIT` (via `rename_existing`)
- Useful for consistency and testing

### `test_speed.cfg`
Macro to verify toolhead motion integrity:
- Moves through large/small patterns at high speed/acceleration
- Checks MCU-reported positions before and after
- Helps detect skipped steps
- Configurable bounds, pattern sizes, iteration count

### `z_tilt_adjust.cfg`
Safe execution wrapper around `Z_TILT_ADJUST`:
- Automatically raises/lifts before and after probing
- Can be chained with leveling or mesh generation macros
- Includes error handling

### `quad_gantry_level.cfg`
Reliable wrapper for `QUAD_GANTRY_LEVEL`:
- Includes pre/post Z-hop
- Ensures clean probing without nozzle dragging
- Works well in combination with `z_tilt_adjust.cfg`

---

## ✅ Usage

1. Clone or copy this repo to your Klipper config folder.
2. In your `printer.cfg`, include the needed files:
   ```ini
   [include print_settings.cfg]
   [include print_start.cfg]
   [include print_end.cfg]
   [include test_speed.cfg]
   ...
   ```
3. Adapt your slicer start/end G-code:
   ```gcode
   START_PRINT
   ...
   END_PRINT
   ```

---

## 💬 RESPOND Message Format

All macros use Klipper's `RESPOND` command with proper message types:
- `TYPE=echo` — for standard logs
- `TYPE=error` — for user-correctable issues
- `TYPE=command` — for suggested manual follow-ups

This ensures full compatibility with:
- **Moonraker**
- **Fluidd**
- **Mainsail**

---

## 🧠 Philosophy

- **Macro logic lives in macros** — not in slicers
- **No hardcoded values** — use variables from `print_settings.cfg`
- **Designed for reliability** — recoverable errors, probing safety, motion checks
- **Hardware-agnostic** — works on bedslingers, CoreXY, Vorons, and more

---

## 📄 License

MIT License — free to use, modify, adapt.

---

## 🙌 Credits

Originally authored by [@thesidoruk](https://github.com/thesidoruk), refined through testing across multiple printers.
