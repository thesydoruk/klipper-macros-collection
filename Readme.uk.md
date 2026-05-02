# Колекція макросів Klipper

Збірка модульних макросів для Klipper: старт/кінець друку, пауза, філамент, шари, checkpoint тощо.

**Повна документація англійською** (кінематика, усі параметри, optional): [Readme.md](Readme.md)

---

## Встановлення

1. Скопіюйте `.cfg` у каталог конфігурації Klipper (або клонуйте репозиторій і підключіть `[include]` на папку).
2. У **`printer.cfg`**:

```ini
[include globals.cfg]
```

3. Для **print checkpoint** додайте **`[save_variables]`** (шлях до файлу змінних — у заголовку `optional/print_checkpoint.cfg`).
4. Додаткові файли з **`optional/`** підключайте окремо, наприклад:

```ini
[include optional/test_speed.cfg]
[include optional/z_tilt_adjust.cfg]
```

`print_checkpoint.cfg` уже підключений через `globals.cfg` (щоб вимкнути — закоментуйте рядок у `globals.cfg`).

---

## Налаштування слайсера

Макроси викликаються з **G-коду, який генерує слайсер** (старт, фініш, зміна шару). Нижче — практичні шаблони.

### PrusaSlicer / SuperSlicer / OrcaSlicer

У сімействі Prusa плейсхолдери виглядають як **`[ім'я]`** або **`{layer_z}`** залежно від місця.

#### Стартовий G-код

**Де:** Налаштування принтера → Користувацький G-код → **Початковий G-код** (або Залежності / Print settings — залежить від версії).

Використовуйте **`PRINT_START`** (не `START_PRINT`). Передайте температури та **область першого шару** для сітки та purge:

```gcode
PRINT_START BED=[first_layer_bed_temperature] EXTRUDER=[first_layer_temperature] \
  MESH_MIN=[first_layer_print_min[0]],[first_layer_print_min[1]] \
  MESH_MAX=[first_layer_print_max[0]],[first_layer_print_max[1]]
```

**Опційно — планувальник шарів (`layers.cfg`):** щоб працювали `total_layer` і `GCODE_AT_LAYER`, можна передати кількість шарів (перевірте точну назву змінної у вашій версії слайсера):

```gcode
PRINT_START BED=[first_layer_bed_temperature] EXTRUDER=[first_layer_temperature] \
  MESH_MIN=[first_layer_print_min[0]],[first_layer_print_min[1]] \
  MESH_MAX=[first_layer_print_max[0]],[first_layer_print_max[1]] \
  LAYERS=[total_layer_count]
```

Якщо слайсер не дає змінної «усього шарів», параметр **`LAYERS=`** можна опустити; тоді використовуйте **`GCODE_AT_LAYER HEIGHT=…`** за потреби.

Не дублюйте повний `G28` і довгий прогрів у слайсері, якщо це вже робить **`PRINT_START`**.

#### Кінцевий G-код

**Де:** Користувацький G-код → **Кінцевий G-код**.

```gcode
PRINT_END
```

#### До / після зміни шару (`layers.cfg`)

**Де:** Налаштування друку → **Перед зміною шару** / **Після зміни шару**.

```gcode
BEFORE_LAYER_CHANGE HEIGHT={layer_z} LAYER={layer_num}
AFTER_LAYER_CHANGE
```

Потрібна секція **`[display_status]`** у `printer.cfg`.

### Тиск / швидкості (velocity)

- Якщо **pressure advance** задаєте в слайсері, він зазвичай шле свій `SET_PRESSURE_ADVANCE`. Макрос **`M900`** і **`variable_pressure_advance_scale`** у `globals.cfg` стосуються саме викликів **M900** з G-коду; щоб не подвоювати логіку, поставте **`variable_pressure_advance_scale: 0`** — тоді **M900** з макросів ігнорується, лишається керування зі слайсера.
- Слайсери з **M201 / M203 / M205** підтримуються через **`velocity.cfg`** (обмеження на **ACCEL** усе ще може блокувати **`LOCK_ACCEL`**).

### Пауза / філамент

- **Зміна філаменту (`M600`):** у цій колекції **`M600`** за замовчуванням немає — у слайсері призначте дію на **`PAUSE`** або додайте свій `[gcode_macro M600]` з викликом `PAUSE`.
- **`PAUSE_AFTER_D`** зазвичай запускають з консолі або іншого макросу, не зі стартового G-коду кожної моделі.

### Cura

У Cura **інші** плейсхолдери, не як у Prusa.

**Початок** (приклад — підлаштуйте координати сітки під стіл):

```gcode
PRINT_START BED={material_bed_temperature_layer_0} EXTRUDER={material_print_temperature_layer_0} MESH_MIN=30,30 MESH_MAX=200,200
```

**Кінець:** `PRINT_END`

**Шари:** у Cura немає одного пари «до/після шару» як у Prusa; потрібні плагіни / post-processing / вставки по висоті, щоб викликати **`BEFORE_LAYER_CHANGE`** / **`AFTER_LAYER_CHANGE`**, якщо ви використовуєте **`layers.cfg`**.

### Bambu Studio та інші хости

Імена змінних і вбудовані послідовності старту відрізняються. Мінімум: або вставте виклик **`PRINT_START`** з явними **BED / EXTRUDER / MESH_***, або повторіть еквівалент прогріву/гомінгу/purge узгоджено з вашим принтером.

### SD-друк і checkpoint

**`print_checkpoint`** і **`RECOVER_PRINT_CHECKPOINT`** розраховані на **`[virtual_sdcard]`** (типово Moonraker). Чистий друк лише по USB з ПК може не заповнювати `virtual_sdcard` — тоді checkpoint не застосовується.

---

## Короткий огляд модулів

| Файл | Призначення |
|------|-------------|
| `globals.cfg` | Змінні `_macro_globals` і `[include …]` усіх основних модулів. |
| `print_start.cfg` / `print_end.cfg` | `PRINT_START` / `PRINT_END`. |
| `state_guard.cfg` | Обгортки `PAUSE` / `RESUME` / `CANCEL_PRINT`, `GLOBAL_STATE`, парк після паузи. |
| `filament.cfg` | Завантаження/вивантаження, `M701`/`M702`, `PAUSE_AFTER_D`. |
| `layers.cfg` | Події по шарах, `GCODE_AT_LAYER`, пауза/швидкість на шарі. |
| `pid.cfg` | `PID_ALL`. |
| `lock_accel.cfg` / `lock_fan.cfg` | Блокування прискорення / вентилятора. |
| `velocity.cfg` | `M201`, `M203`, `M205`, `M900`, `RESET_VELOCITY_LIMITS`. |
| `optional/print_checkpoint.cfg` | Закладки SD та відновлення. |

Деталі команд, параметри й **опис руху кінематики** — у [Readme.md](Readme.md).

---

## Форматування (для розробки)

- У Cursor/VS Code увімкнено збереження з підрізанням пробілів і LF (`.vscode/settings.json`).
- З кореня репозиторію: `python scripts/format_all.py`
- Правила для агентів: `.cursor/rules/`

---

## Ліцензія

MIT — вільне використання та зміни.
