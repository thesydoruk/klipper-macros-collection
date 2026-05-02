# Колекція макросів Klipper

Це практичний набір макросів для Klipper-принтерів. Його мета проста: залишити у слайсері короткий старт і кінець, а поведінку принтера тримати в одному місці - у конфігах Klipper.

Макроси беруть на себе старт друку, завершення, паузу, повернення з паузи, заміну філаменту, дії на шарах, обмеження швидкості й прискорення, захист вентилятора та, за потреби, checkpoint для SD-друку.

Англійська версія: [Readme.md](Readme.md)

## Що входить

Підключіть `globals.cfg` один раз у `printer.cfg`. Він підтягує основні файли та містить спільні налаштування в макросі globals, визначеному в цьому файлі.

```ini
[include globals.cfg]
```

Основні файли, які підключає `globals.cfg`:

- `print_start.cfg`: `PRINT_START` для прогріву, homing, Z tilt / QGL, mesh і purge.
- `print_end.cfg`: `PRINT_END` для retract, підйому Z, park, cooldown і cleanup.
- `state_guard.cfg`: обгортки `PRINT_START`, `PRINT_END`, `PAUSE`, `RESUME`, `CANCEL_PRINT`; стан `GLOBAL_STATE`; повернення з park після паузи.
- `filament.cfg`: `LOAD_FILAMENT`, `UNLOAD_FILAMENT`, `M701`, `M702`, `PAUSE_AFTER_D`.
- `layers.cfg`: slicer layer hooks і заплановані команди: `PAUSE_AT_LAYER`, `SPEED_AT_LAYER`, `FLOW_AT_LAYER`.
- `pid.cfg`: `PID_ALL` для bed і всіх налаштованих extruder-секцій.
- `lock_accel.cfg`: `LOCK_ACCEL` / `UNLOCK_ACCEL` і захищений `SET_VELOCITY_LIMIT`.
- `lock_fan.cfg`: `LOCK_FAN` / `UNLOCK_FAN` і захищені fan-команди.
- `velocity.cfg`: Marlin-style `M201`, `M203`, `M205`, `M900`, `RESET_VELOCITY_LIMITS`.
- `optional/print_checkpoint.cfg`: підключений за замовчуванням; періодично зберігає позицію SD-друку і може підготувати відновлення.

Optional-файли підключайте тільки коли вони справді потрібні:

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

3. Якщо хочете користуватись checkpoint, додайте `[save_variables]` у `printer.cfg`. Приклад є в коментарі на початку `optional/print_checkpoint.cfg`.
4. Перезапустіть Klipper і перевірте консоль на помилки або відсутні залежності.

Якщо checkpoint-макроси взагалі не потрібні, закоментуйте цей рядок у `globals.cfg`:

```ini
[include optional/print_checkpoint.cfg]
```

## Налаштування слайсера

Слайсер має викликати макроси рівня принтера. Не дублюйте повний `G28`, bed mesh і довге очікування прогріву у стартовому G-коді слайсера, якщо це вже робить `PRINT_START`.

### PrusaSlicer, SuperSlicer, OrcaSlicer

Стартовий G-код:

```gcode
PRINT_START BED=[first_layer_bed_temperature] EXTRUDER=[first_layer_temperature] \
  MESH_MIN=[first_layer_print_min[0]],[first_layer_print_min[1]] \
  MESH_MAX=[first_layer_print_max[0]],[first_layer_print_max[1]]
```

Якщо у слайсері є надійний placeholder загальної кількості шарів, передайте його теж:

```gcode
PRINT_START BED=[first_layer_bed_temperature] EXTRUDER=[first_layer_temperature] \
  MESH_MIN=[first_layer_print_min[0]],[first_layer_print_min[1]] \
  MESH_MAX=[first_layer_print_max[0]],[first_layer_print_max[1]] \
  LAYERS=[total_layer_count]
```

Якщо такого placeholder немає, просто не додавайте `LAYERS=`. Команди, заплановані по висоті, все одно працюватимуть.

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

Layer hooks потребують `[display_status]` у `printer.cfg`, бо макроси використовують `SET_PRINT_STATS_INFO`.

### Cura

У Cura інший синтаксис placeholder. Простий приклад старту:

```gcode
PRINT_START BED={material_bed_temperature_layer_0} EXTRUDER={material_print_temperature_layer_0} MESH_MIN=30,30 MESH_MAX=200,200
```

Налаштуйте `MESH_MIN` і `MESH_MAX` під реальну робочу область вашого столу або приберіть їх, якщо не хочете передавати межі mesh зі слайсера.

Кінцевий G-код:

```gcode
PRINT_END
```

У Cura немає такої ж простої пари before/after layer hooks, як у Prusa-family слайсерах. Якщо вам потрібен `layers.cfg`, використовуйте post-processing або вставку G-коду на потрібних шарах, щоб додати `BEFORE_LAYER_CHANGE` і `AFTER_LAYER_CHANGE`.

### Pressure advance, velocity і заміна філаменту

Якщо слайсер генерує `M201`, `M203` або `M205`, `velocity.cfg` перетворює їх на Klipper `SET_VELOCITY_LIMIT`. Зміни прискорення все одно проходять через `lock_accel.cfg`.

`M900 K=...` перетворюється на `SET_PRESSURE_ADVANCE`, якщо `variable_pressure_advance_scale` у `globals.cfg` більше нуля. Встановіть `variable_pressure_advance_scale: 0`, якщо хочете ігнорувати slicer `M900` і керувати pressure advance іншим способом.

`M600` тут не визначений за замовчуванням. Для filament change зі слайсера використовуйте `PAUSE` або додайте власний `M600`, який викличе `PAUSE` і вашу процедуру заміни філаменту.

## Найчастіші команди

`PRINT_START` - основна точка входу зі слайсера. Мінімум потрібні `BED` і `EXTRUDER`; `MESH_MIN` і `MESH_MAX` рекомендовані, якщо слайсер може передати область першого шару.

```gcode
PRINT_START BED=60 EXTRUDER=200 MESH_MIN=30,30 MESH_MAX=200,200
```

`PRINT_END` не має параметрів:

```gcode
PRINT_END
```

Філамент:

```gcode
LOAD_FILAMENT
UNLOAD_FILAMENT
M701 L=80
M702 U=80
```

Пауза після витрати певної довжини філаменту:

```gcode
PAUSE_AFTER_D D=15
PAUSE_AFTER_D D=50 AFTER=UNLOAD
PAUSE_AFTER_D D=30 AFTER=REMIND
```

Планування дій на шарах:

```gcode
GCODE_AT_LAYER LAYER=25 COMMAND="M117 layer 25"
PAUSE_NEXT_LAYER
SPEED_AT_LAYER LAYER=10 SPEED=80
FLOW_AT_LAYER LAYER=20 FLOW=95
```

PID-тюнінг усіх налаштованих heater:

```gcode
PID_ALL
SAVE_CONFIG
```

Блокування прискорення і вентилятора:

```gcode
LOCK_ACCEL ACCEL=3000
UNLOCK_ACCEL

LOCK_FAN SPEED=0.5
UNLOCK_FAN
```

Сумісність із Marlin-style velocity / pressure advance:

```gcode
M201 X3000 Y3000
M203 X150 Y150
M205 X5 Y5
M900 K0.04
RESET_VELOCITY_LIMITS
```

Optional-діагностика:

```gcode
TEST_SPEED SPEED=300 ACCEL=2500 ITERATIONS=4
AUTOTUNE_SGTHRS_PHASE STEPPER=stepper_x ACCEL=3000 FEED=240
```

## Checkpoint і відновлення

`optional/print_checkpoint.cfg` підключений з `globals.cfg`. Він розрахований на друк через Moonraker / Mainsail з `[virtual_sdcard]`, а не на raw USB streaming напряму зі слайсера.

Потрібна конфігурація:

```ini
[save_variables]
filename: ~/printer_data/config/print_checkpoint_vars.cfg
```

Увімкнути періодичне збереження:

```gcode
ENABLE_PRINT_CHECKPOINT
```

Змінити інтервал:

```gcode
ENABLE_PRINT_CHECKPOINT INTERVAL=10
```

Прочитати останній checkpoint:

```gcode
READ_PRINT_CHECKPOINT
```

Вимкнути збереження:

```gcode
DISABLE_PRINT_CHECKPOINT
```

Відновлення зроблене обережно. `RECOVER_PRINT_CHECKPOINT` може завантажити збережений файл і byte offset через virtual SD (`AUTO_SD=1`), зробити `G28 X Y`, виставити логічний стан голови як після паузи, прогрітися і запустити друк через `M24`.

```gcode
RECOVER_PRINT_CHECKPOINT
```

Корисні параметри:

- `AUTO_SD=1`: за замовчуванням; завантажити файл через `M23`, перейти на offset через `M26`, стартувати `M24`.
- `AUTO_SD=0`: підготувати позицію і використати `RESUME`, тільки якщо job уже стоїть на паузі.
- `FILENAME=` і `FILE_POS=`: перевизначити збережені значення.
- `BED=` / `EXTRUDER=` або `EXT=`: перевизначити температури.
- `LIFT=`: перевизначити висоту підйому, яка враховується для логічної Z.
- `SYNC_E=0`: не робити `G92 E...`.
- `SKIP_HEAT=1`: не чекати на прогрів.
- `SKIP_RESUME=1`: зупинитись перед `M24` / `RESUME`.

Будьте обережні: неправильна Z-позиція, неправильний offset у файлі або зсунута модель можуть привести до удару сопла в деталь. Stock Klipper `M23` також може не відкрити файл у підпапці; тоді передайте `FILENAME=` або використайте host-side wrapper script.

## Довідка по кінематиці

Цей розділ навмисно детальний. Якщо майбутня зміна макроса змінює рух голови, цей розділ також треба оновити. Дивіться `.cursor/rules/gcode-kinematics-doc.mdc`.

Умовні позначення: `G90` - абсолютні координати, `G91` - відносні координати, `E` - рух тільки екструдера. Якщо макрос делегує роботу в Klipper built-in команду, наприклад `BED_MESH_CALIBRATE`, `Z_TILT_ADJUST` або `PID_CALIBRATE`, точна траєкторія залежить від вашої конфігурації принтера і самого Klipper.

### `globals.cfg`

Руху немає. Файл тільки підключає інші файли і зберігає змінні.

### `print_start.cfg`

`PRINT_START` виставляє `G90` і `M83`, потім робить повний `G28`. Якщо передані межі mesh, макрос або виконує eddy-гілку (`G1 Z10 F900`, рух у центр mesh на `F6000`, `PROBE_EDDY_NG_TAP`, `EDDYNG_BED_MESH_EXPERIMENTAL`), або викликає `BED_MESH_CALIBRATE` з налаштованими аргументами.

Фаза purge (з межами mesh зі слайсера, якщо передані, інакше відступи від меж осей) очікує вже виставлені `G90` / `M83`: може виконати `G92 E0`, `G1 Z2 F900`, підїзд до підходу purge на `F6000`, `G1 Z` на висоту шару purge з `F300`, prime `G1 E… F300`, `G1` на початок лінії з `F600`, далі черговані `G1` purge-штрихи з X/Y/E на налаштованій швидкості purge і `G92 E0` після екструзії; якщо extruder не може екструдувати або purge пропущено — лише `RESPOND` (без руху голови).

`INIT_LAYER_GCODE`, якщо викликаний через `LAYERS=`, не рухає голову.

### `print_end.cfg`

Якщо XYZ homed, `PRINT_END` перемикається в `G91`, робить retract E на `F1800`, піднімає Z на `F900`, повертається в `G90`, потім їде в налаштований park X/Y на `F6000`.

Якщо осі не homed, macro пропускає retract, lift і park та лише повертає `G90`. Cooldown, mesh clear, fan off, reset flow/speed, reset layer state, disable checkpoint і eddy tap reset не рухають XYZ або E.

### `state_guard.cfg`

Обгортки `PRINT_START` і `PRINT_END` тільки оновлюють стан і передають керування реальним макросам.

`PAUSE` зберігає поточну позицію. Після stock pause і `M400`, якщо XYZ homed і pause lift додатній, він виконує `G91`, піднімає Z на `variable_pause_lift_z` зі швидкістю `variable_pause_lift_feedrate`, повертається в `G90`, потім їде в park X/Y зі швидкістю `variable_pause_park_feedrate`.

`RESUME` повертає голову з pause park, якщо ще очікується повернення з pause park: `G90`, рух у збережені X/Y, потім рух у збережений Z. Після цього очищає цей pending-стан і викликає перейменований stock resume.

`CANCEL_PRINT`, `GLOBAL_STATE`, `STATE_REQUIRE` і пов’язаний перегляд стану не додають руху.

### `filament.cfg`

`LOAD_FILAMENT` і `UNLOAD_FILAMENT` ділять одну реалізацію: `M83` і рух лише E. Load проштовхує `LENGTH`, потім `priming_length`. Unload робить короткий forward move, dwell, shaping-осциляції і довший retract.

`M701` і `M702` спочатку виконують hook паузи для зміни філаменту. Під час друку це означає `PAUSE`. У idle-стані, якщо принтер homed і idle lift увімкнений, виконується `G91`, Z lift і `G90`. Потім ідуть E-рухи load або unload.

`PAUSE_AFTER_D` лише моніторить витрату філаменту. Коли поріг досягнуто, він викликає `PAUSE` і, залежно від `AFTER=`, може викликати `UNLOAD_FILAMENT` або нагадування з beep.

### `layers.cfg`

Layer-макроси самі не рухають принтер. Вони оновлюють print stats і виконують заплановані рядки команд. Якщо ви запланували `PAUSE`, `M220` або будь-який `G1`, рух створює саме ця запланована команда.

### `pid.cfg`

`PID_ALL` не виконує `G0` або `G1`. Він викликає `PID_CALIBRATE` для налаштованих extruder-секцій і bed.

### `lock_accel.cfg`, `lock_fan.cfg`, `velocity.cfg`

Ці макроси не рухають toolhead. Вони змінюють ліміти, стан вентилятора або pressure advance. `velocity.cfg` перетворює `M201`, `M203`, `M205` і `M900` на Klipper-команди лімітів або pressure advance.

### `optional/print_checkpoint.cfg`

Bookmarking-макроси тільки читають статус і зберігають змінні.

`RECOVER_PRINT_CHECKPOINT` з `AUTO_SD=1` скидає / вибирає / seek-ає virtual SD без руху степерів, потім виконує `G28 X Y`, `G90`, їде в pause park X/Y, чекає через `M400` і виконує `SET_KINEMATIC_POSITION X=... Y=... Z=... SET_HOMED=XYZ`, де логічний Z дорівнює збереженому Z друку плюс pause lift. Потім він їде в збережені X/Y друку, опускається до збереженого Z, опційно виконує `M82` і `G92 E...`, гріється і запускає друк через `M24`.

З `AUTO_SD=0` він готує той самий логічний paused state, але фінальне повернення залишає для `RESUME`.

### Optional leveling і діагностика

`optional/z_tilt_adjust.cfg` обгортає stock `Z_TILT_ADJUST`: зберігає стан, очищає mesh якщо він є, робить optional coarse pass з `horizontal_move_z`, фінальний pass і restore state. Рух - це stock Klipper Z tilt probe path.

`optional/quad_gantry_level.cfg` так само обгортає `QUAD_GANTRY_LEVEL`: optional coarse pass, фінальний pass, restore state. Рух - це stock QGL path.

`optional/test_speed.cfg` робить `G28`, опційно QGL і `G28 Z`, переходить у `G90`, рухається біля max XY, робить `G28 X Y`, їде в near-corner reference, піднімається до `Z=bound+10`, виставляє velocity limits, виконує повторювані великі й малі `G0` box/diagonal patterns, відновлює limits, знову робить homing, повертається в corner і відновлює G-code state.

`optional/autotune_sgthrs.cfg` зберігає state, виконує `G28`, рухається на `Z_SAFE`, потім для кожного SG value виконує квадратний і діагональний `G0` pattern навколо центру стола, повертається в reference point, виконує `G28 X Y`, перевіряє drift і в кінці відновлює state.

## Для розробки

У репозиторії є `.editorconfig`, `.gitattributes` і workspace settings для LF, фінального newline і видалення зайвих пробілів. Перед комітом перевіряйте, що змінені `.cfg`, `.md`, `.mdc`, `.ini`, JSON або YAML файли відформатовані цими правилами.

## Ліцензія

MIT. Використовуйте, змінюйте і адаптуйте під свій принтер.
