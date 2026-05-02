# Колекція макросів Klipper

Це набір макросів для Klipper, який прибирає зайву логіку зі слайсера і переносить її в конфіг принтера. Слайсер викликає короткі `PRINT_START` і `PRINT_END`, а макроси вже займаються прогрівом, гомінгом, mesh, purge, паузою, філаментом, шарами, обмеженнями швидкості та, за бажанням, checkpoint для SD-друку.

Англійська документація з повною довідкою по кінематиці: [Readme.md](Readme.md)

## Що входить

Підключається один файл:

```ini
[include globals.cfg]
```

Він підтягує основні модулі:

- `print_start.cfg`: `PRINT_START` для старту друку.
- `print_end.cfg`: `PRINT_END` для завершення друку.
- `state_guard.cfg`: обгортки `PAUSE`, `RESUME`, `CANCEL_PRINT`, стан принтера і повернення з park після паузи.
- `filament.cfg`: `LOAD_FILAMENT`, `UNLOAD_FILAMENT`, `M701`, `M702`, `PAUSE_AFTER_D`.
- `layers.cfg`: дії на шарах, паузи по шару, зміна швидкості або flow на шарі.
- `pid.cfg`: `PID_ALL`.
- `lock_accel.cfg`: блокування зміни прискорення.
- `lock_fan.cfg`: блокування зміни вентилятора.
- `velocity.cfg`: сумісність з Marlin-командами `M201`, `M203`, `M205`, `M900`.
- `optional/print_checkpoint.cfg`: збереження позиції SD-друку і підготовка відновлення.

Інші optional-макроси підключайте вручну:

```ini
[include optional/test_speed.cfg]
[include optional/z_tilt_adjust.cfg]
[include optional/quad_gantry_level.cfg]
[include optional/autotune_sgthrs.cfg]
```

## Встановлення

1. Скопіюйте або склонуйте репозиторій у каталог конфігурації Klipper.
2. Додайте в `printer.cfg`:

```ini
[include globals.cfg]
```

3. Якщо користуєтесь checkpoint, додайте `[save_variables]`. Приклад є у верхньому коментарі файлу `optional/print_checkpoint.cfg`.
4. Перезапустіть Klipper і перевірте консоль на помилки конфігурації.

Якщо checkpoint не потрібен, закоментуйте в `globals.cfg`:

```ini
[include optional/print_checkpoint.cfg]
```

## Налаштування слайсера

Ідея проста: слайсер не має знати всі деталі старту принтера. Він передає температуру, область першого шару і завершує друк одним викликом `PRINT_END`.

### PrusaSlicer, SuperSlicer, OrcaSlicer

Стартовий G-код:

```gcode
PRINT_START BED=[first_layer_bed_temperature] EXTRUDER=[first_layer_temperature] \
  MESH_MIN=[first_layer_print_min[0]],[first_layer_print_min[1]] \
  MESH_MAX=[first_layer_print_max[0]],[first_layer_print_max[1]]
```

Якщо у вашій версії слайсера є стабільна змінна загальної кількості шарів, можна додати `LAYERS=`:

```gcode
PRINT_START BED=[first_layer_bed_temperature] EXTRUDER=[first_layer_temperature] \
  MESH_MIN=[first_layer_print_min[0]],[first_layer_print_min[1]] \
  MESH_MAX=[first_layer_print_max[0]],[first_layer_print_max[1]] \
  LAYERS=[total_layer_count]
```

Якщо такої змінної немає, просто не передавайте `LAYERS`. Для планування за висотою це не критично.

Кінцевий G-код:

```gcode
PRINT_END
```

Перед зміною шару:

```gcode
BEFORE_LAYER_CHANGE HEIGHT={layer_z} LAYER={layer_num}
```

Після зміни шару:

```gcode
AFTER_LAYER_CHANGE
```

Для layer hooks потрібна секція `[display_status]` у `printer.cfg`.

Не дублюйте в слайсері повний `G28`, довгі очікування прогріву, mesh і purge, якщо це вже робить `PRINT_START`.

### Cura

У Cura інші змінні. Базовий приклад:

```gcode
PRINT_START BED={material_bed_temperature_layer_0} EXTRUDER={material_print_temperature_layer_0} MESH_MIN=30,30 MESH_MAX=200,200
```

Підлаштуйте `MESH_MIN` і `MESH_MAX` під робочу область вашого столу. Якщо не хочете передавати межі mesh зі слайсера, їх можна прибрати.

Кінець:

```gcode
PRINT_END
```

У Cura немає такого ж простого поля "before/after layer", як у Prusa-family слайсерах. Якщо вам потрібен `layers.cfg`, використовуйте post-processing або вставку G-коду на потрібних шарах.

### Pressure advance, velocity і M600

Якщо слайсер шле `M201`, `M203` або `M205`, `velocity.cfg` перетворює їх на Klipper `SET_VELOCITY_LIMIT`. Зміни прискорення все одно проходять через `lock_accel.cfg`.

`M900 K=...` перетворюється на `SET_PRESSURE_ADVANCE`, якщо `variable_pressure_advance_scale` у `globals.cfg` більше нуля. Поставте `variable_pressure_advance_scale: 0`, якщо хочете повністю ігнорувати slicer `M900` і керувати pressure advance іншим способом.

`M600` тут спеціально не доданий. Для зміни філаменту зі слайсера використовуйте `PAUSE`, або створіть власний `[gcode_macro M600]`, який викличе `PAUSE` і вашу процедуру заміни.

## Найчастіші команди

Старт і кінець друку:

```gcode
PRINT_START BED=60 EXTRUDER=200 MESH_MIN=30,30 MESH_MAX=200,200
PRINT_END
```

Філамент:

```gcode
LOAD_FILAMENT
UNLOAD_FILAMENT
M701 L=80
M702 U=80
```

Пауза після витрати певної кількості філаменту:

```gcode
PAUSE_AFTER_D D=15
PAUSE_AFTER_D D=50 AFTER=UNLOAD
PAUSE_AFTER_D D=30 AFTER=REMIND
```

Дії на шарах:

```gcode
GCODE_AT_LAYER LAYER=25 COMMAND="M117 layer 25"
PAUSE_NEXT_LAYER
SPEED_AT_LAYER LAYER=10 SPEED=80
FLOW_AT_LAYER LAYER=20 FLOW=95
```

PID:

```gcode
PID_ALL
SAVE_CONFIG
```

Обмеження прискорення і вентилятора:

```gcode
LOCK_ACCEL ACCEL=3000
UNLOCK_ACCEL

LOCK_FAN SPEED=0.5
UNLOCK_FAN
```

Сумісність з Marlin-style командами:

```gcode
M201 X3000 Y3000
M203 X150 Y150
M205 X5 Y5
M900 K0.04
RESET_VELOCITY_LIMITS
```

## Checkpoint і відновлення

`optional/print_checkpoint.cfg` працює з `[virtual_sdcard]`, тобто з типовим Moonraker / Mainsail друком. Якщо друкувати напряму з ПК через USB serial, checkpoint може не мати потрібної позиції файлу.

Потрібен блок у `printer.cfg`:

```ini
[save_variables]
filename: ~/printer_data/config/print_checkpoint_vars.cfg
```

Увімкнути збереження позиції:

```gcode
ENABLE_PRINT_CHECKPOINT
```

Подивитись останню збережену позицію:

```gcode
READ_PRINT_CHECKPOINT
```

Вимкнути:

```gcode
DISABLE_PRINT_CHECKPOINT
```

Відновлення:

```gcode
RECOVER_PRINT_CHECKPOINT
```

За замовчуванням `RECOVER_PRINT_CHECKPOINT` працює в режимі `AUTO_SD=1`: вибирає файл через virtual SD, ставить byte offset, робить `G28 X Y`, ставить логічну Z-позицію як "збережений Z + висота паузи", повертає сопло до збережених XY/Z, гріє і запускає `M24`.

Корисні параметри:

- `FILENAME=` і `FILE_POS=` - вручну перевизначити файл і позицію.
- `BED=` / `EXTRUDER=` - температури для відновлення.
- `LIFT=` - висота, яку враховувати як підйом після паузи.
- `SYNC_E=0` - не робити `G92 E...`.
- `SKIP_HEAT=1` - не чекати прогріву.
- `SKIP_RESUME=1` - підготувати позицію, але не запускати друк.

Важливо: це не магія і не гарантія безпечного power-loss recovery. Якщо модель зсунута, Z неправильний або offset у файлі не той, сопло може врізатися в деталь.

## Рух кінематики

Повний опис руху для кожного макроса підтримується в англійському [Readme.md](Readme.md). Коротко:

- `PRINT_START` робить `G28`, за потреби mesh / probe, потім purge-рухи з E.
- `PRINT_END` при homed XYZ робить retract, Z-lift і park.
- `PAUSE` піднімає Z і їде в park; `RESUME` повертається до збережених XY/Z.
- `LOAD_FILAMENT` / `UNLOAD_FILAMENT` рухають лише E.
- `layers.cfg` сам не рухає принтер, але виконує заплановані команди.
- `velocity.cfg`, `lock_accel.cfg`, `lock_fan.cfg`, `pid.cfg` не роблять `G0` / `G1`.
- `RECOVER_PRINT_CHECKPOINT` рухає XY/Z і використовує `SET_KINEMATIC_POSITION`, тому його треба запускати тільки якщо ви розумієте стан принтера після збою.

## Для розробки

Перед завершенням змін у `.cfg`, `.md`, `.mdc`, `.ini`, JSON або YAML:

```shell
python scripts/format_all.py
```

У репозиторії є `.editorconfig`, `.gitattributes` і налаштування VS Code/Cursor для LF, final newline і видалення зайвих пробілів.

## Ліцензія

MIT. Можна використовувати, змінювати і адаптувати під свій принтер.
