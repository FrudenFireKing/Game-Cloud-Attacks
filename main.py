from turtle import mode

import pygame
import random
import json
import os
import math
import sys

pygame.init()

WIDTH, HEIGHT = 960, 640
FPS = 60
TITLE = "СПУТНИКС — Облако атакует"

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption(TITLE)
CLOCK = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 22)
SMALL = pygame.font.SysFont("arial", 17)
BIG = pygame.font.SysFont("arial", 34, bold=True)
HUGE = pygame.font.SysFont("arial", 52, bold=True)

SAVE_FILE = "saves/save.json"

ENDING_FRAMES_DIR = "assets/ending"
ENDING_FPS = 24
ENDING_FRAME_COUNT = 190

ending_frame = 0
ending_last_update = 0
ending_finished = False

# ---------------------------------------------------------
# COLORS
# ---------------------------------------------------------
BG = (10, 14, 22)
PANEL = (20, 27, 39)
PANEL2 = (28, 37, 52)
TEXT = (235, 241, 245)
MUTED = (155, 168, 181)
ACCENT = (255, 151, 58)
CYAN = (70, 220, 230)
GREEN = (100, 210, 125)
RED = (235, 85, 85)
YELLOW = (245, 215, 90)
WHITE = (255, 255, 255)

# ---------------------------------------------------------
# GAME DATA
# ---------------------------------------------------------
chapters = {
    0: "ПРОЛОГ — ПЕРВОЕ СЕНТЯБРЯ",
    1: "ГЛАВА 1 — ПОДЗЕМНЫЕ ОАЗИСЫ",
    2: "ГЛАВА 2 — РОЙ",
    3: "ГЛАВА 3 — СИГНАЛ",
    4: "ГЛАВА 4 — ТАЙГА 2.0",
    5: "ГЛАВА 5 — ОРБИТА",
}

state = {
    "chapter": 0,
    "scene": "menu",
    "samples": 0,
    "choice": None,
    "discovered": [],
    "chapter1_progress": 0,
    "chapter2_progress": 0,
    "chapter3_progress": 0,
    "chapter4_progress": 0,
    "chapter5_progress": 0,
}

# ---------------------------------------------------------
# DEBUG: запуск нужной главы из терминала
# ---------------------------------------------------------

DEBUG_CHAPTER = None

if len(sys.argv) > 1:
    argument = sys.argv[1].lower()

    if argument.startswith("-chapter"):
        try:
            DEBUG_CHAPTER = int(argument.replace("-chapter", ""))
        except ValueError:
            DEBUG_CHAPTER = None

# ---------------------------------------------------------
# ASSET HELPERS
# ---------------------------------------------------------
def load_image(path, size=None, fallback_color=(80, 90, 105)):
    try:
        image = pygame.image.load(path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except (pygame.error, FileNotFoundError):
        if size is None:
            size = (64, 64)
        image = pygame.Surface(size, pygame.SRCALPHA)
        image.fill(fallback_color)
        return image

# Спрайты главы 2 — Рой
swarm_ground = load_image("assets/swarm/ground.png", (WIDTH, HEIGHT))
swarm_sprite = load_image("assets/swarm/swarm.png", (110, 90))
trap_sprite = load_image("assets/swarm/trap.png", (48, 48))


# Глава 3 — космос и спутники
orbit_space_bg = load_image(
    "assets/orbit/space.png",
    (WIDTH, HEIGHT)
)

orbit_earth = load_image(
    "assets/orbit/earth.png",
    (260, 260)
)

orbit_satellite = load_image(
    "assets/orbit/satellite.png",
    (48, 38)
)

# Глава 4 — тайга
taiga_bg = load_image(
    "assets/taiga/taiga.png",
    (WIDTH, HEIGHT)
)


# ---------------------------------------------------------
# LABORATORY SPRITES
# ---------------------------------------------------------
LAB_ASSETS = "assets/laboratory"

lab_sprites = {
    "computer": [
        load_image(f"{LAB_ASSETS}/work_station/work_station.png"),
        load_image(f"{LAB_ASSETS}/work_station/left_work.png"),
        load_image(f"{LAB_ASSETS}/work_station/right_work.png"),
    ],
    "samples": [
        load_image(f"{LAB_ASSETS}/sample_table/table.png"),
        load_image(f"{LAB_ASSETS}/sample_table/soil.png"),
        load_image(f"{LAB_ASSETS}/sample_table/organic.png"),
        load_image(f"{LAB_ASSETS}/sample_table/ice_crystal.png"),
    ],
    "map": [
        load_image(f"{LAB_ASSETS}/map/table_map.png"),
        load_image(f"{LAB_ASSETS}/map/close_map.png"),
    ],
    "radar": [
        load_image(f"{LAB_ASSETS}/control_panel/remote.png"),
        load_image(f"{LAB_ASSETS}/control_panel/left.png"),
        load_image(f"{LAB_ASSETS}/control_panel/right.png"),
    ],
    "junix": [
        load_image(f"{LAB_ASSETS}/junix/junix.png"),
        load_image(f"{LAB_ASSETS}/junix/left.png"),
        load_image(f"{LAB_ASSETS}/junix/right.png"),
    ],
    "microscope": [
        load_image(f"{LAB_ASSETS}/microscope/microscope_table.png"),
        load_image(f"{LAB_ASSETS}/microscope/microscope.png"),
        load_image(f"{LAB_ASSETS}/microscope/spores.png"),
        load_image(f"{LAB_ASSETS}/microscope/bacterial_culture.png"),
        load_image(f"{LAB_ASSETS}/microscope/cell_wall.png"),
    ],
    "aurora": [
        load_image(f"assets/characters/aurora/lab.png"),
    ]
}

# Индекс текущего крупного плана
inspect_frame_index = 0
blink_alpha = 0
blink_start_time = 0
microscope_stage = 0

# Загрузка эмоций персонажей (neutral, happy, worried)
def load_character_emotions(name_folder, size=(120, 150), fallback_color=(55, 95, 120)):
    base_path = f"assets/characters/{name_folder}/dialogue"
    return {
        "neutral": load_image(f"{base_path}/neutral.png", size, fallback_color),
        "happy": load_image(f"{base_path}/happy.png", size, fallback_color),
        "worried": load_image(f"{base_path}/worried.png", size, fallback_color),
    }

# Загрузка анимационных фреймов движения Вани
vanya_movement_frames = {
    "down": [load_image(f"assets/characters/vanya/movement/down{i}.png", (36, 52), (70, 130, 160)) for i in range(1, 5)],
    "right": [load_image(f"assets/characters/vanya/movement/right{i}.png", (36, 52), (70, 130, 160)) for i in range(1, 4)],
    "up": [load_image(f"assets/characters/vanya/movement/up{i}.png", (36, 52), (70, 130, 160)) for i in range(1, 5)],
    "down_right": [load_image(f"assets/characters/vanya/movement/down_right{i}.png", (36, 52), (70, 130, 160)) for i in range(1, 4)],
    "up_right": [load_image(f"assets/characters/vanya/movement/up_right{i}.png", (36, 52), (70, 130, 160)) for i in range(1, 4)],
}
vanya_current_dir = "down"

vanya_emotions = load_character_emotions("vanya")
grisha_emotions = load_character_emotions("grisha", fallback_color=(100, 75, 55))
aurora_emotions = load_character_emotions("aurora", fallback_color=(100, 65, 125))

def draw_text(text, x, y, font=FONT, color=TEXT, center=False):
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    SCREEN.blit(surface, rect)
    return rect


def draw_wrapped_text(text, x, y, font, color, max_width, line_spacing=6):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()

        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    for i, line in enumerate(lines):
        rendered = font.render(line, True, color)
        SCREEN.blit(rendered, (x, y + i * (font.get_height() + line_spacing)))

def draw_panel(rect, color=PANEL, border=ACCENT, radius=12):
    pygame.draw.rect(SCREEN, color, rect, border_radius=radius)
    pygame.draw.rect(SCREEN, border, rect, 2, border_radius=radius)

def button(rect, text, active=True):
    color = PANEL2 if active else (35, 40, 48)
    border = ACCENT if active else MUTED
    draw_panel(rect, color, border)
    draw_text(text, rect.centerx, rect.centery, SMALL, TEXT if active else MUTED, True)

# ---------------------------------------------------------
# SAVE / LOAD
# ---------------------------------------------------------
def save_game():
    os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
    temp_file = SAVE_FILE + ".tmp"
    backup_file = SAVE_FILE + ".bak"
    data = dict(state)
    data["save_version"] = 2
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        if os.path.exists(SAVE_FILE):
            try: os.replace(SAVE_FILE, backup_file)
            except OSError: pass
        os.replace(temp_file, SAVE_FILE)
        return True
    except (OSError, TypeError, ValueError):
        try:
            if os.path.exists(temp_file): os.remove(temp_file)
        except OSError: pass
        return False

def load_game():
    global state
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
        state.update(saved)
        return True
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return False

# ---------------------------------------------------------
# PLAYER / TOP-DOWN EXPLORATION & DETAILED LAB INSPECTION
# ---------------------------------------------------------
player = pygame.Rect(470, 420, 36, 52)
player_speed = 8
anim_timer = 0
vanya_frame_idx = 0
vanya_last_dir = "down"
vanya_last_anim_time = pygame.time.get_ticks()

lab_objects = [
    {"id": "computer", "name": "Рабочая станция", "rect": pygame.Rect(-20, 40, 320, 170),
     "text": "На экране открыта карта экспедиции и данные Ровера-1.",
     "sub_items": ["Лог ошибок ИИ", "Схема датчиков", "Архив телеметрии"]},
    {"id": "samples", "name": "Стол образцов", "rect": pygame.Rect(650, 105, 190, 100),
     "text": "Контейнеры с пробами. Часть образцов ещё предстоит проанализировать.",
     "sub_items": ["Образец почвы №1", "Органический осадок", "Кристаллический скол"]},
    {"id": "map", "name": "Карта Сибири", "rect": pygame.Rect(50, 300, 210, 120),
     "text": "На карте отмечена «мёртвая зона» и маршрут будущей экспедиции.",
     "sub_items": ["Сектор А", "Сектор Б (Аномалия)", "Глубинные разломы"]},
    {"id": "radar", "name": "Пульт «Зоркого»", "rect": pygame.Rect(780, 250, 90, 220),
     "text": "Спутник «Зоркий» готов получать задания на сканирование.",
     "sub_items": ["Оптический канал", "Тепловизор", "Ролокатор льда"]},
    {"id": "junix", "name": "Терминал JuniX", "rect": pygame.Rect(380, 60, 160, 75),
     "text": "JuniX управляет спутниковой связью и ретрансляцией.",
     "sub_items": ["Ретранслятор 1", "Шлюз пакетов", "Протокол шифрования"]},
    {"id": "microscope", "name": "Микроскоп", "rect": pygame.Rect(350, 465, 180, 85),
     "text": "Под микроскопом видны необычные микроорганизмы.",
     "sub_items": ["Споры неизвестного типа", "Бактериальная культура", "Клеточная оболочка"]},
    {"id": "aurora", "name": "Аврора", "rect": pygame.Rect(700, 490, 45, 90),
     "text": "Аврора: «Перед выездом проверь оборудование ещё раз.»",
     "sub_items": ["Статус миссии", "Проверка скафандров", "Допуск к выходу"]},
]

lab_required = 5
near_object = None
inspecting_object = None  # Полноэкранный режим изучения предмета/шкафа

def reset_player():
    player.x, player.y = 460, 400

def update_exploration():
    global anim_timer, vanya_frame_idx, vanya_current_dir, vanya_last_dir, vanya_last_anim_time
    keys = pygame.key.get_pressed()
    dx = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
    dy = int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP])

    if dx > 0 and dy >0:
        vanya_current_dir = "down_right"
    elif dx > 0 and dy < 0:
        vanya_current_dir = "up_right"
    elif dx > 0:
        vanya_current_dir = "right"
    elif dx < 0 and dy > 0:
        vanya_current_dir = "down_right"
    elif dx < 0 and dy < 0:
        vanya_current_dir = "up_right"
    elif dx < 0:
        vanya_current_dir = "right"
    elif dy > 0:
        vanya_current_dir = "down"
    elif  dy < 0:
        vanya_current_dir = "up"

    if vanya_current_dir != vanya_last_dir:
        vanya_frame_idx = 0
        vanya_last_dir = vanya_current_dir
        vanya_last_anim_time = pygame.time.get_ticks()

    if dx or dy:
        now = pygame.time.get_ticks()
        if now - vanya_last_anim_time >= 90:
            frames = vanya_movement_frames.get(vanya_current_dir, [])
            if frames:
                vanya_frame_idx = (vanya_frame_idx + 1) % len(frames)
            else:
                vanya_frame_idx = 0
            vanya_last_anim_time = now
    else:
        vanya_frame_idx = 0

    if dx and dy:
        speed = player_speed / math.sqrt(2)
    else:
        speed = player_speed

    move_x = int(dx * speed)
    move_y = int(dy * speed)

    next_rect = player.copy()
    next_rect.x += move_x

    if not any(next_rect.colliderect(obj["rect"].inflate(10, 10)) for obj in lab_objects):
        player.x = next_rect.x

    next_rect = player.copy()
    next_rect.y += move_y

    if not any(next_rect.colliderect(obj["rect"].inflate(10, 10)) for obj in lab_objects):
        player.y = next_rect.y
    player.clamp_ip(pygame.Rect(35, 85, WIDTH - 70, HEIGHT - 120))

    global near_object
    near_object = None
    for obj in lab_objects:
        if player.inflate(20, 20).colliderect(obj["rect"]):
            near_object = obj
            break


def draw_lab():
    SCREEN.fill((10, 17, 27))

    
    lab_floor = load_image(f"{LAB_ASSETS}/lab_floor.png")
    lab_floor = pygame.transform.scale(lab_floor, (WIDTH, HEIGHT))

    SCREEN.blit(lab_floor, (0, 0))


    # Верхняя панель интерфейса
    pygame.draw.rect(SCREEN, (9, 17, 28), (0, 0, WIDTH, 70))
    pygame.draw.line(SCREEN, CYAN, (0, 69), (WIDTH, 69), 2)
    pygame.draw.circle(SCREEN, CYAN, (25, 27), 5)

    draw_text("НАУЧНО-ИССЛЕДОВАТЕЛЬСКАЯ ЛАБОРАТОРИЯ",
              45, 15, BIG, TEXT)
    draw_text(f"ИЗУЧЕНО: {len(state['discovered'])}/{lab_required}",
              WIDTH - 150, 25, SMALL, CYAN, True)


    # Оборудование
    for obj in lab_objects:
        rect = obj["rect"]
        
        sprite_list = lab_sprites.get(obj["id"], [])

        if sprite_list:
            sprite = sprite_list[0]

            if obj["id"] == "radar":
                sprite = pygame.transform.rotate(sprite, -90)

            elif obj["id"] == "computer":
                sprite = pygame.transform.rotate(sprite, 10)
            
            elif obj["id"] == "samples":
                sprite = pygame.transform.rotate(sprite, -20)

            sprite = pygame.transform.smoothscale(
                sprite, (rect.width, rect.height)
            )
            SCREEN.blit(sprite, rect)
        else:
            pygame.draw.rect(SCREEN, (25, 36, 47), rect)

        # Тонкая рамка при наведении
        if near_object is obj:
            pygame.draw.rect(SCREEN, CYAN, rect.inflate(8, 8), 2, border_radius=8)
            pygame.draw.circle(SCREEN, CYAN, (rect.right + 7, rect.top - 5), 4)

        draw_text(
            obj["name"], rect.centerx, rect.bottom + 9,
            SMALL, CYAN if near_object is obj else TEXT, True
        )

    # Персонаж
    frames_list = (
        vanya_movement_frames.get(vanya_current_dir)
        or vanya_movement_frames.get("down", [])
    )
    if not frames_list:
        frames_list = [load_image("", (36, 52), (70, 130, 160))]

    current_vanya_sprite = frames_list[vanya_frame_idx % len(frames_list)]
    keys = pygame.key.get_pressed()
    is_left = keys[pygame.K_a] or keys[pygame.K_LEFT]
    is_right = keys[pygame.K_d] or keys[pygame.K_RIGHT]

    if is_left and not is_right:
        current_vanya_sprite = pygame.transform.flip(
            current_vanya_sprite, True, False
        )

    vanya_size = (
        int(current_vanya_sprite.get_width() * 1.25),
        int(current_vanya_sprite.get_height() * 1.25)
    )
    current_vanya_sprite = pygame.transform.scale(
        current_vanya_sprite, vanya_size
    )
    SCREEN.blit(
        current_vanya_sprite,
        current_vanya_sprite.get_rect(center=player.center)
    )

    # Подсказка взаимодействия
    if near_object:
        hint_rect = pygame.Rect(WIDTH // 2 - 195, HEIGHT - 62, 390, 42)
        draw_panel(hint_rect, PANEL, CYAN, radius=10)
        draw_text(
            f"[ E ]  Изучить: {near_object['name']}",
            WIDTH // 2, hint_rect.centery, SMALL, TEXT, True
        )

    if len(state["discovered"]) >= lab_required:
        draw_panel(pygame.Rect(250, 82, 460, 38), (25, 58, 52), GREEN)
        draw_text(
            "Оборудование изучено — поговорите с Авророй",
            WIDTH // 2, 101, SMALL, WHITE, True
        )



def draw_inspect_screen():
    if not inspecting_object:
        return

    obj_id = inspecting_object["id"]
    frames = lab_sprites.get(obj_id, [])

    if not frames:
        return

    # Ограничиваем индекс доступными кадрами
    if obj_id == "microscope" and microscope_stage == 0:
        frame_index = min(1, len(frames) - 1)
    else:
        frame_index = max(
            0,
            min(inspect_frame_index, len(frames) - 1)
        )

    image = frames[frame_index]

    # Затемняем лабораторию
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    SCREEN.blit(overlay, (0, 0))

    # Изображение почти на весь экран
    margin = 30
    max_width = WIDTH - margin * 2
    max_height = HEIGHT - 100

    scale = min(
        max_width / image.get_width(),
        max_height / image.get_height()
    )

    new_size = (
        int(image.get_width() * scale),
        int(image.get_height() * scale)
    )
    image = pygame.transform.smoothscale(image, new_size)

    image_rect = image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    SCREEN.blit(image, image_rect)
    
    if obj_id != "microscope":
        text_box = pygame.Rect(35, HEIGHT - 105, WIDTH - 70, 65)
        draw_panel(text_box, PANEL, CYAN, radius=8)
        draw_text(
            inspecting_object.get("text", ""),
            WIDTH // 2, text_box.centery,
            SMALL, TEXT, True
        )

    # Подсказка снизу
    if obj_id == "microscope" and microscope_stage == 0:
        draw_text("E — изучить образец   |   ESC — назад",
                WIDTH // 2, HEIGHT - 20, SMALL, MUTED, True)
    else:
        draw_text("← → — осмотреть   |   ESC — назад",
                WIDTH // 2, HEIGHT - 20, SMALL, MUTED, True)
    
    elapsed = pygame.time.get_ticks() - blink_start_time
    blink_alpha = max(0, 255 - int(elapsed * 255 / 120))

    if blink_alpha > 0:
        blink = pygame.Surface((WIDTH, HEIGHT))
        blink.fill((0, 0, 0))
        blink.set_alpha(blink_alpha)
        SCREEN.blit(blink, (0, 0))

def interact_lab():
    global inspecting_object, inspect_frame_index
    global inspect_blink_until, microscope_stage

    # Если экран изучения уже открыт
    if inspecting_object:
        if inspecting_object["id"] == "microscope" and microscope_stage == 0:
            microscope_stage = 1
            inspect_frame_index = 2
            inspect_blink_until = pygame.time.get_ticks() + 115
        return

    if not near_object:
        return

    # Аврора
    if near_object["id"] == "aurora":
        if len(state["discovered"]) >= lab_required:
            start_dialogue("chapter0_dialogue")
        else:
            inspecting_object = near_object
            inspect_frame_index = 1
        return

    inspecting_object = near_object
    inspect_frame_index = 1
    microscope_stage = 0
    inspect_blink_until = pygame.time.get_ticks() + 115

    if near_object["id"] not in state["discovered"]:
        state["discovered"].append(near_object["id"])
        save_game()

# ---------------------------------------------------------
# DIALOGUE SYSTEM WITH 2D NOVEL PORTRAITS
# ---------------------------------------------------------
dialogues = {
    "chapter0_dialogue": [
        ("Аврора", "worried", "Теперь мы знаем, что подземная зона намного сложнее, чем казалось."),
        ("Гриша", "neutral", "Нужно обследовать её подробнее. Но сначала надо решить, как действовать."),
        ("Ваня", "happy", "Я подготовил фреймы движения для роверов, всё пройдёт отлично!"),
    ],
    "chapter1_intro": [
        ("МЧС", "neutral", "Команда, нам нужна полная карта подземных полостей."),
        ("Аврора", "neutral", "«Зоркий» покажет структуру сверху. Роверы смогут проверить доступные маршруты."),
        ("Ваня", "happy", "Тогда начнём с самых стабильных участков."),
    ],
    "chapter2_intro": [
        ("Аврора", "worried", "Спутники обнаружили движение огромного роя."),
        ("Ваня", "neutral", "Если правильно расставить ловушки, можно изменить его траекторию."),
    ],
    "chapter3_intro": [
        ("Ваня", "worried", "Этот сигнал не похож на обычные помехи."),
        ("Аврора", "neutral", "Сначала определим источник. Потом решим, что делать."),
    ],
    "chapter4_intro": [
        ("Гриша", "happy", "Оазисы живы. Значит, восстановление экосистемы возможно."),
        ("Аврора", "neutral", "Но вмешиваться нужно осторожно. Один дисбаланс может уничтожить всю систему."),
    ],
    "chapter5_intro": [
        ("Аврора", "happy", "Эксперимент с дрозофилами одобрен."),
        ("Гриша", "neutral", "Наконец-то мы работаем с орбитальной станцией."),
    ],
}

dialogue_index = 0
dialogue_key = None
dialogue_choice = None

def start_dialogue(key):
    global dialogue_key, dialogue_index
    dialogue_key = key
    dialogue_index = 0
    state["scene"] = key

def draw_dialogue():
    SCREEN.fill((9, 13, 20))

    for y in range(0, HEIGHT, 32):
        pygame.draw.line(SCREEN, (15, 23, 34), (0, y), (WIDTH, y))

    if dialogue_key not in dialogues:
        return

    speaker, emotion, text = dialogues[dialogue_key][dialogue_index]
    
    # Выбор эмоции персонажа для новеллы
    if speaker == "Ваня":
        portrait = vanya_emotions.get(emotion, vanya_emotions["neutral"])
    elif speaker == "Аврора":
        portrait = aurora_emotions.get(emotion, aurora_emotions["neutral"])
    else:
        portrait = grisha_emotions.get(emotion, grisha_emotions["neutral"])

    # Увеличенный портрет персонажа (новелла-стайл слева)
    pygame.draw.rect(SCREEN, (28, 36, 48), (50, 50, 220, 420), border_radius=16)
    SCREEN.blit(pygame.transform.scale(portrait, (220, 360)), (50, 80))
    draw_text(speaker, 160, 435, BIG, ACCENT, True)

    # Окно текста диалога
    draw_panel(pygame.Rect(290, 320, 630, 240), PANEL)
    draw_wrapped_text(
        text,
        320, 350,
        FONT, TEXT,
        max_width=560,
        line_spacing=6
    )

    draw_text("SPACE — продолжить", 700, 535, SMALL, MUTED)

def advance_dialogue():
    global dialogue_index
    if dialogue_key not in dialogues:
        return

    if dialogue_index < len(dialogues[dialogue_key]) - 1:
        dialogue_index += 1
        return

    finish_dialogue()

def finish_dialogue():
    global dialogue_key

    if dialogue_key == "chapter0_dialogue":
        state["scene"] = "chapter0_choice"
    elif dialogue_key == "aurora_aftermath":
        state["scene"] = "chapter1"
        start_chapter1()
    elif dialogue_key == "chapter1_intro":
            state["scene"] = "chapter1"
            start_chapter1()
            if state.get("choice") == 1:
                pass
    elif dialogue_key == "chapter2_intro":
        state["scene"] = "chapter2"
        start_chapter2()
    elif dialogue_key == "chapter3_intro":
        state["scene"] = "chapter3"
        start_chapter3()
    elif dialogue_key == "chapter4_intro":
        state["scene"] = "chapter4"
        start_chapter4()
    elif dialogue_key == "chapter5_intro":
        state["scene"] = "chapter5"
        start_chapter5()

    save_game()

def draw_choice(title, options):
    SCREEN.fill((10, 14, 22))
    draw_text(title, WIDTH // 2, 110, BIG, ACCENT, True)

    for i, option in enumerate(options):
        rect = pygame.Rect(180, 210 + i * 100, 600, 70)
        button(rect, option)
    draw_text("Выбор изменит порядок следующих событий.", WIDTH // 2, 440, SMALL, MUTED, True)

def handle_chapter0_choice(mouse_pos):
    global dialogue_choice
    options = [
        "Проверить маршруты и продолжить исследование",
        "Сначала усилить связь со спутниками",
    ]

    for i in range(2):
        rect = pygame.Rect(180, 210 + i * 100, 600, 70)
        if rect.collidepoint(mouse_pos):
            dialogue_choice = i
            state["choice"] = i
            start_dialogue("chapter1_intro")
            return
        
def draw_signal_qte():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    SCREEN.blit(overlay, (0, 0))

    draw_panel(
        pygame.Rect(140, 100, 680, 440),
        PANEL,
        CYAN
    )

    draw_text(
        "ВОССТАНОВЛЕНИЕ СИГНАЛА",
        WIDTH // 2,
        140,
        BIG,
        CYAN,
        True
    )

    draw_text(
        signal_labels[signal_stage],
        WIDTH // 2,
        205,
        FONT,
        TEXT,
        True
    )

    # Этапы
    for i in range(3):
        x = 270 + i * 200
        y = 290

        if i < signal_stage:
            color = GREEN
            text = "✓"
        elif i == signal_stage:
            color = CYAN
            text = pygame.key.name(signal_sequence[i]).upper()
        else:
            color = MUTED
            text = pygame.key.name(signal_sequence[i]).upper()

        pygame.draw.rect(
            SCREEN,
            (30, 35, 45),
            (x - 55, y - 45, 110, 90),
            border_radius=12
        )

        pygame.draw.rect(
            SCREEN,
            color,
            (x - 55, y - 45, 110, 90),
            3,
            border_radius=12
        )

        draw_text(
            text,
            x,
            y,
            BIG,
            color,
            True
        )

    draw_text(
        f"Этап {signal_stage + 1}/3",
        WIDTH // 2,
        410,
        FONT,
        ACCENT,
        True
    )

    draw_text(
        "Неправильная клавиша сбросит настройку",
        WIDTH // 2,
        460,
        SMALL,
        MUTED,
        True
    )

    draw_text(
        "Q → E → SPACE",
        WIDTH // 2,
        500,
        SMALL,
        CYAN,
        True
    )

# ---------------------------------------------------------
# PROLOGUE WITH QTE MECHANICS
# ---------------------------------------------------------
prologue_step = 0
prologue_qte_active = False
prologue_qte_key_idx = 0
prologue_qte_keys = [pygame.K_q, pygame.K_e, pygame.K_SPACE]
prologue_qte_labels = ["БЫСТРЫЙ СХВАТ: Удержать консоль (Нажми Q)", "БЫСТРЫЙ СХВАТ: Экстренный тормоз (Нажми E)", "БЫСТРЫЙ СХВАТ: Стабилизация (Нажми SPACE)"]

prologue_messages = [
    "Первое сентября. Университетская лаборатория готовит новую экспедицию.",
    "Гриша впервые получает доступ к исследовательскому роверу.",
    "Внезапно под полом лаборатории раздается гул — провал под землю!",
    "QTE-ИСПЫТАНИЕ: Удерживайте систему от обрушения!",
    "На тепловой камере появляется человек в подземной зоне.",
    "А затем датчики фиксируют огромное скопление насекомых (рой).",
    "Спасательная операция завершена. Команда сообщает о находке в МЧС.",
]

def draw_prologue():
    SCREEN.fill((11, 16, 24))
    draw_text("ПРОЛОГ — ПЕРВОЕ СЕНТЯБРЯ", WIDTH // 2, 80, BIG, ACCENT, True)

    draw_panel(pygame.Rect(130, 160, 700, 270), PANEL)

    # Текст текущего события пролога
    draw_text(
        prologue_messages[prologue_step],
        WIDTH // 2,
        270,
        FONT,
        TEXT,
        True
    )

    if prologue_step == 3:
        # QTE в прологе
        draw_panel(pygame.Rect(200, 310, 560, 90), (45, 30, 30), RED)

        draw_text(
            prologue_qte_labels[prologue_qte_key_idx],
            WIDTH // 2,
            355,
            SMALL,
            WHITE,
            True
        )
    else:
        draw_text(
            "SPACE — продолжить",
            WIDTH // 2,
            350,
            SMALL,
            MUTED,
            True
        )

def advance_prologue():
    global prologue_step, prologue_qte_active
    if prologue_step == 3:
        return # Ждем нажатия QTE клавиши

    if prologue_step < len(prologue_messages) - 1:
        prologue_step += 1
        if prologue_step == 3:
            prologue_qte_active = True
    else:
        state["chapter"] = 0
        state["scene"] = "lab"
        reset_player()
        save_game()

def handle_prologue_qte(key):
    global prologue_qte_key_idx, prologue_qte_active, prologue_step
    if not prologue_qte_active:
        return

    if not (0 <= prologue_qte_key_idx < len(prologue_qte_keys)):
        prologue_qte_active = False
        return

    if key == prologue_qte_keys[prologue_qte_key_idx]:
        prologue_qte_key_idx += 1

        if prologue_qte_key_idx >= len(prologue_qte_keys):
            prologue_qte_active = False
            prologue_qte_key_idx = 0
            prologue_step += 1 # Переходим к следующему сообщению пролога


def draw_ending_video():
    global ending_frame
    global ending_last_update
    global ending_finished

    now = pygame.time.get_ticks()

    if now - ending_last_update >= 1000 // ENDING_FPS:
        ending_frame += 1
        ending_last_update = now

    if ending_frame >= ENDING_FRAME_COUNT:
        ending_frame = ENDING_FRAME_COUNT - 1
        ending_finished = True

    frame_path = os.path.join(
        ENDING_FRAMES_DIR,
        f"frame_{ending_frame + 1:04d}.png"
    )

    if os.path.exists(frame_path):
        frame = pygame.image.load(frame_path).convert()
        frame = pygame.transform.scale(frame, (WIDTH, HEIGHT))
        SCREEN.blit(frame, (0, 0))
# ---------------------------------------------------------
# CHAPTER 1 — UNDERGROUND OASES
# ---------------------------------------------------------
rover = pygame.Rect(120, 430, 42, 30)
rover_speed = 4
rover_samples = []

# Спрайты главы 1 — подземные оазисы
UNDERGROUND_ASSETS = "assets/underground"

underground_ground = load_image(
    f"{UNDERGROUND_ASSETS}/ground.png",
    (WIDTH, HEIGHT)
)

underground_permafrost = load_image(
    f"{UNDERGROUND_ASSETS}/permafrost.png",
    (WIDTH, HEIGHT)
)

underground_safe_zone = load_image(
    f"{UNDERGROUND_ASSETS}/safe_zone.png"
)

underground_rocks = [
    load_image(f"{UNDERGROUND_ASSETS}/samples/rock{i}.png")
    for i in range(1, 7)
]

# Анимация движения ровера
ROVER_SPRITE_SIZE = (64, 48)
ROVER_ANIMATION_DELAY = 140  # Задержка между кадрами, мс

rover_movement_frames = {
    "down": [
        load_image(f"assets/characters/rover/movement/down{i}.png",
                   ROVER_SPRITE_SIZE)
        for i in range(1, 3)
    ],
    "up": [
        load_image(f"assets/characters/rover/movement/up{i}.png",
                   ROVER_SPRITE_SIZE)
        for i in range(1, 3)
    ],
    "right": [
        load_image(f"assets/characters/rover/movement/right{i}.png",
                   ROVER_SPRITE_SIZE)
        for i in range(1, 3)
    ],
    "down_right": [
        load_image(f"assets/characters/rover/movement/down_right{i}.png",
                   ROVER_SPRITE_SIZE)
        for i in range(1, 3)
    ],
    "up_right": [
        load_image(f"assets/characters/rover/movement/up_right{i}.png",
                   ROVER_SPRITE_SIZE)
        for i in range(1, 3)
    ],
}

rover_current_dir = "down"
rover_frame_idx = 0
rover_last_frame_update = 0
rover_flip_x = False
rover_moving = False

crack_zones = [
    pygame.Rect(300, 170, 130, 35),
    pygame.Rect(520, 300, 160, 40),
    pygame.Rect(700, 150, 100, 35),
]
safe_zones = [
    pygame.Rect(80, 100, 170, 170),
    pygame.Rect(450, 100, 160, 160),
    pygame.Rect(740, 350, 150, 160),
]
chapter1_samples_needed = 6
qte_active = False
qte_sequence = [pygame.K_q, pygame.K_t, pygame.K_e]
qte_char_names = ["Q", "T", "E"]
qte_step_idx = 0         # Индекс текущей клавиши (0 -> Q, 1 -> T, 2 -> E)
qte_clicks_needed = 8    # Сколько раз нужно нажать каждую клавишу
qte_current_clicks = 0   # Текущие клики на этапе
qte_timer = 120          # Таймер на каждый этап (2 секунды при 60 FPS)
qte_labels = ["ЗАБЛОКИРОВАТЬ КОЛЁСА", "ВЫДВИНУТЬ ЯКОРЬ", "ПЕРЕДАТЬ ТЯГУ"]
# Новые QTE режимы: "mash" (многократное нажатие), "hold" (удержание)
qte_mode = "mash"
qte_hold_progress = 0
qte_hold_required = 120
qte_hold_key = pygame.K_SPACE
# Сигнальная QTE последовательность для главы 3
signal_stage = 0
signal_sequence = [
    pygame.K_q,
    pygame.K_e,
    pygame.K_SPACE
]
signal_labels = [
    "НАСТРОЙТЕ ЛЕВЫЙ ДИАПАЗОН",
    "НАСТРОЙТЕ ПРАВЫЙ ДИАПАЗОН",
    "ЗАФИКСИРУЙТЕ СИГНАЛ"
]

# 
balance_position = 0.0
balance_target = 0.0
balance_wave = 0
balance_wave_time = 0
balance_wave_duration = 180
balance_speed = 0.018
balance_zone_width = 0.35

def start_chapter1(reset_progress=True):
    global rover_samples, qte_active, qte_step_idx, qte_current_clicks, qte_timer
    rover.x, rover.y = 100, 450
    qte_active = False
    qte_step_idx = 0
    qte_current_clicks = 0
    qte_timer = 120
    if reset_progress:
        rover_samples = []
        state["chapter1_progress"] = 0
    else:
        count = max(0, min(chapter1_samples_needed, state.get("chapter1_progress", 0)))
        rover_samples = list(range(count))

def move_rover():
    global rover_current_dir
    global rover_frame_idx
    global rover_last_frame_update
    global rover_flip_x
    global rover_moving

    keys = pygame.key.get_pressed()

    dx = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - \
         int(keys[pygame.K_a] or keys[pygame.K_LEFT])

    dy = int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - \
         int(keys[pygame.K_w] or keys[pygame.K_UP])

    rover_moving = dx != 0 or dy != 0

    # Определяем направление движения
    if rover_moving:
        if dx != 0 and dy != 0:
            rover_current_dir = (
                "down_right" if dy > 0 else "up_right"
            )
            rover_flip_x = dx < 0

        elif dx != 0:
            rover_current_dir = "right"
            rover_flip_x = dx < 0

        elif dy > 0:
            rover_current_dir = "down"
            rover_flip_x = False

        else:
            rover_current_dir = "up"
            rover_flip_x = False

        # Переключаем кадры анимации
        now = pygame.time.get_ticks()

        if now - rover_last_frame_update >= ROVER_ANIMATION_DELAY:
            frames = rover_movement_frames[rover_current_dir]
            rover_frame_idx = (rover_frame_idx + 1) % len(frames)
            rover_last_frame_update = now

    else:
        # Когда ровер стоит, показываем первый кадр
        rover_frame_idx = 0
        rover_last_frame_update = pygame.time.get_ticks()

    # Перемещаем ровер
    if dx and dy:
        speed = rover_speed / math.sqrt(2)
    else:
        speed = rover_speed

    rover.x += int(dx * speed)
    rover.y += int(dy * speed)

    # Не даём роверу выехать за границы уровня
    rover.clamp_ip(pygame.Rect(25, 100, WIDTH - 50, HEIGHT - 135))


def draw_chapter1():
    # Фон подземной пещеры
    SCREEN.blit(underground_ground, (0, 0))

    # Текстура вечной мерзлоты поверх фона
    SCREEN.blit(underground_permafrost, (0, 0))

    # Заголовок и счётчик образцов
    draw_text("ГЛАВА 1 — ПОДЗЕМНЫЕ ОАЗИСЫ", 25, 22, BIG)
    draw_text(
        f"Пробы: {len(rover_samples)}/{chapter1_samples_needed}",
        735, 30, SMALL, CYAN
    )


    for zone in safe_zones:
        zone_image = pygame.transform.smoothscale(
            underground_safe_zone,
            zone.size
        )
        SCREEN.blit(zone_image, zone.topleft)


    
    sample_positions = [
        (180, 160), (400, 250), (610, 180),
        (800, 260), (330, 470), (700, 500)
    ]

    for i, pos in enumerate(sample_positions):
        if i not in rover_samples:
            rock = underground_rocks[i]

            rock_size = (
                max(12, int(rock.get_width() * 0.3)),
                max(12, int(rock.get_height() * 0.3))
            )

            rock = pygame.transform.smoothscale(rock, rock_size)
            rock_rect = rock.get_rect(center=pos)

            # Мягкое свечение под образцом
            glow = pygame.Surface((rock_rect.width + 18, rock_rect.height + 18), pygame.SRCALPHA)
            pygame.draw.ellipse(
                glow,
                (60, 210, 220, 35),
                glow.get_rect()
            )
            SCREEN.blit(glow, glow.get_rect(center=pos))

            SCREEN.blit(rock, rock_rect)

            # Компактная подпись над образцом
            draw_text(
                "ПРОБА",
                pos[0], rock_rect.top - 12,
                SMALL, (105, 225, 235), True
            )

    # Выбираем кадр анимации ровера
    frames = rover_movement_frames.get(
        rover_current_dir,
        rover_movement_frames["down"]
    )

    rover_sprite = frames[rover_frame_idx % len(frames)]

    # Для движения влево отражаем спрайт по горизонтали
    if rover_flip_x:
        rover_sprite = pygame.transform.flip(
            rover_sprite, True, False
        )

    # Рисуем спрайт в центре хитбокса ровера
    rover_sprite_rect = rover_sprite.get_rect(
        center=rover.center
    )

    SCREEN.blit(rover_sprite, rover_sprite_rect)

    if qte_active:
        draw_qte()
        return

    if len(rover_samples) >= chapter1_samples_needed:
        draw_panel(pygame.Rect(240, 565, 480, 50), (30, 55, 45), GREEN)
        draw_text("Все полости обследованы. SPACE — к «Провалу»",
                  WIDTH // 2, 590, SMALL, WHITE, True)

def collect_sample():
    sample_positions = [
        (180, 160), (400, 250), (610, 180),
        (800, 260), (330, 470), (700, 500)
    ]
    for i, pos in enumerate(sample_positions):
        if i not in rover_samples and rover.collidepoint(pos):
            rover_samples.append(i)
            state["chapter1_progress"] = len(rover_samples)
            save_game()
            break

def start_qte(mode="mash"):
    global qte_active, qte_step_idx, qte_current_clicks
    global qte_timer, qte_mode, qte_hold_progress
    global balance_position, balance_target
    global balance_wave, balance_wave_time
    global balance_speed, balance_zone_width

    qte_active = True
    qte_step_idx = 0
    qte_current_clicks = 0
    qte_timer = 120

    qte_mode = mode
    qte_hold_progress = 0
    
    global signal_stage

    if mode == "signal":
        signal_stage = 0
    
    if mode == "balance":
        balance_position = 0.0
        balance_target = 0.0
        balance_wave = 1
        balance_wave_time = 0

        balance_speed = 0.010
        balance_zone_width = 0.35
    
def advance_after_qte():
    current_scene = state["scene"]
    if current_scene == "chapter1_boss":
        state["scene"] = "chapter2_intro"
        start_dialogue("chapter2_intro")
    elif current_scene == "chapter2_qte":
        state["scene"] = "chapter3_intro"
        start_dialogue("chapter3_intro")
    elif current_scene == "chapter3_qte":
        state["scene"] = "chapter4_intro"
        start_dialogue("chapter4_intro")
    elif current_scene == "chapter4_qte":
        state["scene"] = "chapter5_intro"
        start_dialogue("chapter5_intro")
    save_game()
    
def draw_balance_qte():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 175))
    SCREEN.blit(overlay, (0, 0))

    draw_panel(
        pygame.Rect(120, 100, 720, 420),
        PANEL,
        ACCENT
    )

    draw_text(
        "СТАБИЛИЗАЦИЯ ЭКОСИСТЕМЫ",
        WIDTH // 2,
        140,
        BIG,
        ACCENT,
        True
    )

    draw_text(
        f"ВОЛНА {balance_wave} / 4",
        WIDTH // 2,
        185,
        FONT,
        TEXT,
        True
    )

    draw_text(
        "Удерживайте баланс в зелёной зоне",
        WIDTH // 2,
        220,
        FONT,
        MUTED,
        True
    )

    # Шкала
    bar_x = 190
    bar_y = 300
    bar_width = 580
    bar_height = 45

    # Фон шкалы
    pygame.draw.rect(
        SCREEN,
        (45, 45, 55),
        (bar_x, bar_y, bar_width, bar_height),
        border_radius=10
    )

    # Безопасная зона
    center_x = bar_x + bar_width // 2
    safe_width = int(bar_width * balance_zone_width)

    safe_rect = pygame.Rect(
        center_x - safe_width // 2,
        bar_y,
        safe_width,
        bar_height
    )

    pygame.draw.rect(
        SCREEN,
        (50, 150, 80),
        safe_rect,
        border_radius=10
    )

    # Текущая позиция
    player_x = int(
        center_x +
        balance_position * (bar_width // 2)
    )

    pygame.draw.circle(
        SCREEN,
        WHITE,
        (player_x, bar_y + bar_height // 2),
        13
    )

    pygame.draw.circle(
        SCREEN,
        ACCENT,
        (player_x, bar_y + bar_height // 2),
        13,
        3
    )

    draw_text(
        "A",
        bar_x - 35,
        bar_y + 22,
        BIG,
        TEXT,
        True
    )

    draw_text(
        "D",
        bar_x + bar_width + 35,
        bar_y + 22,
        BIG,
        TEXT,
        True
    )

    draw_text(
        "← A                 D →",
        WIDTH // 2,
        390,
        FONT,
        MUTED,
        True
    )

    draw_text(
        "Не дайте индикатору выйти за зелёную зону",
        WIDTH // 2,
        445,
        SMALL,
        TEXT,
        True
    )

def handle_qte_key(key):
    global qte_active, qte_step_idx, qte_current_clicks, qte_timer
    if not qte_active:
        return
    
    if qte_mode == "hold":
        return

    if not (0 <= qte_step_idx < len(qte_sequence)):
        qte_active = False
        return

    target_key = qte_sequence[qte_step_idx]

    if key == target_key:
        qte_current_clicks += 1
        if qte_current_clicks >= qte_clicks_needed:
            qte_step_idx += 1
            qte_current_clicks = 0
            
            if qte_step_idx >= len(qte_sequence):
                qte_active = False
                advance_after_qte()
            else:
                qte_timer = 120
    else:
        qte_timer -= 30

        if qte_timer <= 0:
            qte_active = False

            current_scene = state["scene"]

            if current_scene == "chapter1_boss":
                state["resume_scene"] = "chapter1"

            elif current_scene == "chapter2_qte":
                state["resume_scene"] = "chapter2"

            elif current_scene == "chapter3_qte":
                state["resume_scene"] = "chapter3"

            elif current_scene == "chapter4_qte":
                state["resume_scene"] = "chapter4"

            state["scene"] = "menu"
            save_game()
            
def handle_signal_qte(key):
    global qte_active, signal_stage, qte_timer

    if not qte_active:
        return

    if key == signal_sequence[signal_stage]:
        signal_stage += 1
        qte_timer = 120

        if signal_stage >= len(signal_sequence):
            qte_active = False
            advance_after_qte()
    else:
        signal_stage = 0
        qte_timer = 120
        
def handle_balance_qte(key):
    global balance_position

    if not qte_active:
        return

    if key == pygame.K_a:
        balance_position -= 0.2

    elif key == pygame.K_d:
        balance_position += 0.2

    balance_position = max(-1.0, min(1.0, balance_position))

def draw_qte():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 165))
    SCREEN.blit(overlay, (0, 0))

    draw_panel(pygame.Rect(170, 140, 620, 370), PANEL, RED)
    draw_text("КОМБИНИРОВАННОЕ QTE!", WIDTH // 2, 175, BIG, RED, True)
    
    current_letter = qte_char_names[min(qte_step_idx, len(qte_char_names) - 1)]
    draw_text(f"Быстро жмите клавишу: [{current_letter}]", WIDTH // 2, 225, FONT, TEXT, True)

    bar_width = 400
    progress = min(1.0, qte_current_clicks / qte_clicks_needed)
    pygame.draw.rect(SCREEN, (40, 40, 50), (280, 275, bar_width, 30), border_radius=8)
    pygame.draw.rect(SCREEN, GREEN, (280, 275, int(bar_width * progress), 30), border_radius=8)
    draw_text(f"{qte_current_clicks} / {qte_clicks_needed}", WIDTH // 2, 290, SMALL, WHITE, True)

    steps_display = " -> ".join([f"[{c}]" if i == qte_step_idx else c for i, c in enumerate(qte_char_names)])
    draw_text(f"Цепочка: {steps_display}", WIDTH // 2, 335, SMALL, ACCENT, True)

    seconds_left = max(0, qte_timer / FPS)
    draw_text(f"Осталось времени: {seconds_left:.1f} сек", WIDTH // 2, 380, FONT, ACCENT, True)

def draw_hold_qte():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 165))
    SCREEN.blit(overlay, (0, 0))

    draw_panel(pygame.Rect(170, 140, 620, 370), PANEL, RED)

    draw_text(
        "УДЕРЖИВАЙТЕ КЛАВИШУ!",
        WIDTH // 2,
        175,
        BIG,
        RED,
        True
    )

    # Какая клавиша
    key_rect = pygame.Rect(WIDTH // 2 - 75, 215, 150, 70)

    pygame.draw.rect(SCREEN, (35, 40, 50), key_rect, border_radius=12)
    pygame.draw.rect(SCREEN, RED, key_rect, 3, border_radius=12)

    draw_text(
        "SPACE",
        WIDTH // 2,
        250,
        BIG,
        WHITE,
        True
    )

    # Прогресс удержания
    progress = min(
        1.0,
        qte_hold_progress / qte_hold_required
    )

    bar_x = 240
    bar_y = 330
    bar_width = 440
    bar_height = 30

    pygame.draw.rect(
        SCREEN,
        (40, 40, 50),
        (bar_x, bar_y, bar_width, bar_height),
        border_radius=8
    )

    pygame.draw.rect(
        SCREEN,
        RED,
        (
            bar_x,
            bar_y,
            int(bar_width * progress),
            bar_height
        ),
        border_radius=8
    )

    draw_text(
        f"{int(progress * 100)}%",
        WIDTH // 2,
        385,
        FONT,
        WHITE,
        True
    )

    if pygame.key.get_pressed()[qte_hold_key]:
        draw_text(
            "УДЕРЖИВАЙТЕ...",
            WIDTH // 2,
            430,
            SMALL,
            TEXT,
            True
        )
    else:
        draw_text(
            "НАЖМИТЕ И УДЕРЖИВАЙТЕ",
            WIDTH // 2,
            430,
            SMALL,
            MUTED,
            True
        )

# ---------------------------------------------------------
# CHAPTER 2 — SWARM
# ---------------------------------------------------------
trap_positions = [(170, 180), (360, 350), (560, 170), (760, 350)]
selected_traps = []
swarm_pos = [820, 120]

def start_chapter2():
    global selected_traps, swarm_pos
    selected_traps = []
    swarm_pos = [820, 120]
    state["chapter2_progress"] = 0


def draw_chapter2():
    # Фон пещеры
    SCREEN.blit(swarm_ground, (0, 0))

    # Затемнение верхней панели для читаемости
    header = pygame.Surface((WIDTH, 70), pygame.SRCALPHA)
    header.fill((10, 15, 22, 190))
    SCREEN.blit(header, (0, 0))

    draw_text("ГЛАВА 2 — РОЙ", 25, 18, BIG)
    draw_text(
        f"Ловушки: {len(selected_traps)}/4",
        WIDTH - 200, 28, SMALL, CYAN
    )

    # Место, куда рой должен быть направлен
    field_rect = pygame.Rect(720, 430, 170, 110)
    field_surface = pygame.Surface(
        field_rect.size, pygame.SRCALPHA
    )
    pygame.draw.rect(
        field_surface, (40, 210, 220, 35),
        field_surface.get_rect(), border_radius=12
    )
    pygame.draw.rect(
        field_surface, (70, 220, 230, 150),
        field_surface.get_rect(), 2, border_radius=12
    )
    SCREEN.blit(field_surface, field_rect.topleft)
    draw_text(
        "ЗОНА НАПРАВЛЕНИЯ",
        field_rect.centerx, field_rect.bottom + 12,
        SMALL, CYAN, True
    )

    # Точки установки ловушек
    for i, pos in enumerate(trap_positions):
        if i in selected_traps:
            # Установленная ловушка
            trap_rect = trap_sprite.get_rect(center=pos)
            SCREEN.blit(trap_sprite, trap_rect)
        else:
            # Подсказка, куда можно поставить ловушку
            pygame.draw.circle(
                SCREEN, (60, 220, 230), pos, 22, 2
            )
            pygame.draw.circle(
                SCREEN, (60, 220, 230), pos, 3
            )
            draw_text(
                str(i + 1), pos[0], pos[1] - 32,
                SMALL, WHITE, True
            )

    # Рой
    swarm_rect = swarm_sprite.get_rect(center=swarm_pos)
    SCREEN.blit(swarm_sprite, swarm_rect)

    # Инструкция внизу
    footer = pygame.Surface((WIDTH, 54), pygame.SRCALPHA)
    footer.fill((10, 15, 22, 205))
    SCREEN.blit(footer, (0, HEIGHT - 54))

    if len(selected_traps) == 4:
        draw_text(
            "Цепь ловушек готова. SPACE — начать испытание",
            WIDTH // 2, HEIGHT - 27, SMALL, WHITE, True
        )
    else:
        draw_text(
            "Кликните по четырём точкам, чтобы установить ловушки",
            WIDTH // 2, HEIGHT - 27, SMALL, WHITE, True
        )

def click_chapter2(pos):
    for i, point in enumerate(trap_positions):
        if math.dist(pos, point) < 28 and i not in selected_traps:
            selected_traps.append(i)
            state["chapter2_progress"] = len(selected_traps)
            save_game()
            return

# ---------------------------------------------------------
# CHAPTER 3 — SIGNAL
# ---------------------------------------------------------
radio_nodes = [
    pygame.Rect(100, 180, 130, 70),
    pygame.Rect(350, 350, 130, 70),
    pygame.Rect(600, 180, 130, 70),
    pygame.Rect(780, 360, 130, 70),
]
radio_order = []
signal_stage = 0

signal_sequence = [
    pygame.K_q,
    pygame.K_e,
    pygame.K_SPACE
]

signal_labels = [
    "НАСТРОЙТЕ ЛЕВЫЙ ДИАПАЗОН",
    "НАСТРОЙТЕ ПРАВЫЙ ДИАПАЗОН",
    "ЗАФИКСИРУЙТЕ СИГНАЛ"
]

def start_chapter3():
    radio_order.clear()
    state["chapter3_progress"] = 0


def draw_chapter3():
    # Космический фон
    SCREEN.blit(orbit_space_bg, (0, 0))

    # Затемнение сверху для читаемости заголовка
    header_overlay = pygame.Surface((WIDTH, 135), pygame.SRCALPHA)
    header_overlay.fill((5, 10, 25, 175))
    SCREEN.blit(header_overlay, (0, 0))

    draw_text("ГЛАВА 3 — СИГНАЛ", 25, 22, BIG)

    draw_text(
        "Выстройте ретрансляцию вокруг зон помех.",
        WIDTH // 2, 78, SMALL, MUTED, True
    )

    draw_text(
        "ПОСЛЕДОВАТЕЛЬНОСТЬ: 1 → 3 → 2 → 4",
        WIDTH // 2, 110, FONT, YELLOW, True
    )

    # Земля вместо кругов помех
    earth_rect = orbit_earth.get_rect(center=(490, 330))
    SCREEN.blit(orbit_earth, earth_rect)

    # Спутники
    for i, rect in enumerate(radio_nodes):
        active = i in radio_order

        # Полупрозрачная подложка блока
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        panel.fill((10, 22, 42, 205))
        SCREEN.blit(panel, rect.topleft)

        # Рамка спутника
        border_color = GREEN if active else CYAN
        pygame.draw.rect(
            SCREEN, border_color, rect,
            2, border_radius=10
        )

        # Изображение спутника
        satellite_rect = orbit_satellite.get_rect(
            center=(rect.centerx, rect.y + 19)
        )
        SCREEN.blit(orbit_satellite, satellite_rect)

        # Название и статус
        draw_text(
            f"Спутник {i + 1}",
            rect.centerx, rect.y + 43,
            SMALL, TEXT, True
        )

        draw_text(
            "OK" if active else "OFF",
            rect.centerx, rect.y + 59,
            SMALL, GREEN if active else MUTED, True
        )

    draw_text(
        f"Активировано: {len(radio_order)}/4",
        WIDTH // 2, 560, FONT, CYAN, True
    )

    if len(radio_order) == 4:
        draw_panel(
            pygame.Rect(280, 585, 400, 42),
            (35, 65, 55), GREEN
        )
        draw_text(
            "Источник триангулирован. SPACE — продолжить.",
            WIDTH // 2, 606, SMALL, WHITE, True
        )

def click_chapter3(pos):
    required_order = [0, 2, 1, 3]

    for i, rect in enumerate(radio_nodes):
        if rect.collidepoint(pos) and i not in radio_order:

            if i == required_order[len(radio_order)]:
                radio_order.append(i)
                state["chapter3_progress"] = len(radio_order)
                save_game()
            else:
                # Неправильный спутник — сбрасываем последовательность
                radio_order.clear()
                state["chapter3_progress"] = 0
                save_game()

            return
# ---------------------------------------------------------
# CHAPTER 4 — ECOSYSTEM
# ---------------------------------------------------------
organisms = [
    ("Микроорганизмы", 1),
    ("Насекомые-санитары", 2),
    ("Хищники", 3),
    ("Фитофаги", 4),
]
ecosystem = [0, 0, 0, 0]

def start_chapter4():
    global ecosystem
    ecosystem = [0, 0, 0, 0]
    state["chapter4_progress"] = 0

def draw_chapter4():
    SCREEN.blit(taiga_bg, (0, 0))
    draw_text("ГЛАВА 4 — ТАЙГА 2.0", 25, 22, BIG)
    draw_text("Соберите устойчивую экосистему.", WIDTH // 2, 75, SMALL, MUTED, True)

    for i, (name, _) in enumerate(organisms):
        rect = pygame.Rect(120, 140 + i * 90, 720, 65)
        draw_panel(rect, PANEL2)
        draw_text(name, rect.x + 20, rect.centery, FONT, TEXT, False)
        draw_text(str(ecosystem[i]), rect.right - 90, rect.centery, BIG, CYAN, True)

        minus = pygame.Rect(rect.right - 170, rect.y + 12, 45, 40)
        plus = pygame.Rect(rect.right - 115, rect.y + 12, 45, 40)
        button(minus, "-")
        button(plus, "+")

    good = ecosystem == [3, 2, 1, 2]
    index = abs(ecosystem[0] - 3) + abs(ecosystem[1] - 2) + abs(ecosystem[2] - 1) + abs(ecosystem[3] - 2)

    draw_text(f"Индекс баланса: {index}", WIDTH // 2, 525, FONT,
              GREEN if good else YELLOW, True)

    if good:
        draw_panel(pygame.Rect(250, 570, 460, 45), (35, 70, 45), GREEN)
        draw_text("Баланс восстановлен. SPACE — финальный этап.",
                  WIDTH // 2, 592, SMALL, WHITE, True)

def click_chapter4(pos):
    for i in range(4):
        y = 140 + i * 90

        minus = pygame.Rect(670, y + 12, 45, 40)
        plus = pygame.Rect(725, y + 12, 45, 40)

        if plus.collidepoint(pos):
            ecosystem[i] = min(5, ecosystem[i] + 1)

        elif minus.collidepoint(pos):
            ecosystem[i] = max(0, ecosystem[i] - 1)

        else:
            continue

        state["ecosystem"] = ecosystem.copy()
        state["chapter4_progress"] = sum(ecosystem)
        save_game()
        return

# ---------------------------------------------------------
# CHAPTER 5 — ORBIT
# ---------------------------------------------------------

orbit_step = 0

orbit_actions = [
    "НАЙТИ ТЕРМИНАЛ",
    "ВОССТАНОВИТЬ ПИТАНИЕ",
    "ВОССТАНОВИТЬ СВЯЗЬ",
    "ЗАПУСТИТЬ ЦЕНТРАЛЬНЫЙ МОДУЛЬ",
]

orbit_walls = [
    pygame.Rect(120, 150, 700, 20),
    pygame.Rect(120, 460, 700, 20),

    pygame.Rect(120, 150, 20, 330),
    pygame.Rect(800, 150, 20, 330),

    pygame.Rect(250, 150, 20, 170),
    pygame.Rect(250, 380, 20, 100),

    pygame.Rect(400, 250, 20, 230),

    pygame.Rect(550, 150, 20, 170),
    pygame.Rect(550, 380, 20, 100),

    pygame.Rect(680, 250, 20, 230),
]

orbit_objects = [
    {
        "name": "Терминал",
        "type": "terminal",
        "step": 0,
        "rect": pygame.Rect(180, 220, 45, 45),
        "color": (70, 150, 190),
        "used": False
    },
    {
        "name": "Энергоблок",
        "type": "power",
        "step": 1,
        "rect": pygame.Rect(330, 170, 45, 45),
        "color": (210, 170, 60),
        "used": False
    },
    {
        "name": "Пульт связи",
        "type": "radio",
        "step": 2,
        "rect": pygame.Rect(620, 320, 45, 45),
        "color": (100, 180, 120),
        "used": False
    },
    {
        "name": "Центральный модуль",
        "type": "core",
        "step": 3,
        "rect": pygame.Rect(720, 180, 45, 45),
        "color": (180, 100, 210),
        "used": False
    }
]

near_orbit_object = None
orbit_terminal_open = False
orbit_power_open = False
orbit_radio_open = False
orbit_core_open = False
orbit_final = False


def start_chapter5(reset_progress=True):
    global orbit_step
    global near_orbit_object
    global orbit_terminal_open
    global orbit_power_open
    global orbit_radio_open
    global orbit_core_open
    global orbit_final

    if reset_progress:
        orbit_step = 0
        state["chapter5_progress"] = 0

        for obj in orbit_objects:
            obj["used"] = False
    else:
        orbit_step = state.get("chapter5_progress", 0)

        for obj in orbit_objects:
            obj["used"] = obj["step"] < orbit_step

    near_orbit_object = None
    orbit_terminal_open = False
    orbit_power_open = False
    orbit_radio_open = False
    orbit_core_open = False
    orbit_final = False


    # Начальная позиция Вани
    player.x = 170
    player.y = 400

    # Начальное направление
    global vanya_current_dir, vanya_frame_idx
    global vanya_last_dir, vanya_last_anim_time

    vanya_current_dir = "down"
    vanya_last_dir = "down"
    vanya_frame_idx = 0
    vanya_last_anim_time = pygame.time.get_ticks()


def draw_chapter5():
    if orbit_station_bg:
        SCREEN.blit(orbit_station_bg, (0, 0))
    else:
        SCREEN.fill((7, 12, 22))

    draw_text(
        "ГЛАВА 5 — ОРБИТА",
        WIDTH // 2,
        45,
        BIG,
        ACCENT,
        True
    )

    draw_text(
        "ОРБИТАЛЬНАЯ ЭКСПЕРИМЕНТАЛЬНАЯ СТАНЦИЯ",
        WIDTH // 2,
        85,
        SMALL,
        MUTED,
        True
    )

    # Станция
    pygame.draw.rect(
        SCREEN,
        (35, 45, 60),
        (80, 120, 800, 400),
        border_radius=20
    )

    pygame.draw.rect(
        SCREEN,
        (15, 25, 38),
        (110, 150, 740, 340),
        border_radius=15
    )

    # Отсеки
    for wall in orbit_walls:
        pygame.draw.rect(
            SCREEN,
            (38, 48, 62),
            wall,
            border_radius=4
        )

        pygame.draw.rect(
            SCREEN,
            (70, 82, 96),
            wall,
            2,
            border_radius=4
        )

    for obj in orbit_objects:
        if obj["used"]:
            color = (45, 55, 65)
        elif obj["step"] == orbit_step:
            color = obj["color"]
        else:
            color = (55, 65, 75)

        sprite = orbit_sprites.get(obj["type"])

        if sprite:
            # Подгоняем картинку под размер объекта
            scaled_sprite = pygame.transform.scale(
                sprite,
                (obj["rect"].width, obj["rect"].height)
            )

            SCREEN.blit(scaled_sprite, obj["rect"])
        else:
            pygame.draw.rect(
                SCREEN,
                color,
                obj["rect"]
            )

        if not obj["used"] and obj["step"] == orbit_step:
            pulse = (pygame.time.get_ticks() // 450) % 2

            if pulse == 0:
                pygame.draw.rect(
                    SCREEN,
                    ACCENT,
                    obj["rect"].inflate(10, 10),
                    2,
                    border_radius=8
                )
    
    # Игрок
    frames_list = (
        vanya_movement_frames.get(vanya_current_dir)
        or vanya_movement_frames.get("down", [])
    )
    if not frames_list:
        frames_list = [load_image("", (36, 52), (70, 130, 160))]
    current_vanya_sprite = frames_list[
        vanya_frame_idx % len(frames_list)
    ]
    keys = pygame.key.get_pressed()
    is_left = (
        keys[pygame.K_a]
        or keys[pygame.K_LEFT]
    )
    if is_left and not (
        keys[pygame.K_d]
        or keys[pygame.K_RIGHT]
    ):
        current_vanya_sprite = pygame.transform.flip(
            current_vanya_sprite,
            True,
            False
        )
    SCREEN.blit(
        current_vanya_sprite,
        current_vanya_sprite.get_rect(center=player.center)
    )
    
    if near_orbit_object:
        draw_panel(
            pygame.Rect(300, 570, 360, 48),
            PANEL
        )
        action_text = (
            f"E — Исследовать {near_orbit_object['name']}"
            if not near_orbit_object["used"]
            else f"{near_orbit_object['name']} уже исследован"
        )
        draw_text(
            action_text,
            480,
            594,
            SMALL,
            TEXT,
            True
        )
    
    # ---------------------------------------------------------
    # ФОНАРИК
    # ---------------------------------------------------------

    darkness = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    darkness.fill((0, 0, 0, 238))

    px, py = player.center

    pygame.draw.circle(
        darkness,
        (0, 0, 0, 0),
        (px, py),
        80
    )

    SCREEN.blit(darkness, (0, 0))

    # Текущая задача
    draw_panel(
        pygame.Rect(180, 85, 600, 55),
        PANEL,
        ACCENT
    )

    if orbit_step < 3:
        draw_text(
            f"ЭТАП {orbit_step + 1}/3",
            200,
            112,
            SMALL,
            MUTED
        )

        draw_text(
            orbit_actions[orbit_step],
            480,
            112,
            FONT,
            ACCENT,
            True
        )
    else:
        draw_text(
            "ЭКСПЕРИМЕНТ СПАСЁН",
            WIDTH // 2,
            562,
            FONT,
            GREEN,
            True
        )
    """
    draw_text(
        "WASD / стрелки — перемещение",
        WIDTH // 2,
        610,
        SMALL,
        MUTED,
        True
    )
    """
    
    # Окно терминала
    if orbit_terminal_open:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        SCREEN.blit(overlay, (0, 0))

        terminal_rect = pygame.Rect(150, 120, 660, 400)

        draw_panel(
            terminal_rect,
            PANEL,
            ACCENT
        )

        draw_text(
            "ТЕРМИНАЛ СТАНЦИИ",
            WIDTH // 2,
            165,
            BIG,
            ACCENT,
            True
        )

        draw_text(
            "СИСТЕМА ДИАГНОСТИКИ",
            WIDTH // 2,
            215,
            SMALL,
            MUTED,
            True
        )

        draw_text(
            "Питание: ОТКЛЮЧЕНО",
            210,
            270,
            FONT,
            TEXT
        )

        draw_text(
            "Связь: НЕДОСТУПНА",
            210,
            315,
            FONT,
            TEXT
        )

        draw_text(
            "Центральный модуль: ОЖИДАНИЕ",
            210,
            360,
            FONT,
            TEXT
        )

        draw_text(
            "Аварийный режим станции: АКТИВЕН",
            210,
            405,
            FONT,
            (255, 100, 100)
        )

        draw_text(
            "E — продолжить",
            WIDTH // 2,
            470,
            SMALL,
            ACCENT,
            True
        )
        
    # Окно энергоблока
    elif orbit_power_open:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 110))
        SCREEN.blit(overlay, (0, 0))

        power_rect = pygame.Rect(150, 120, 660, 400)

        draw_panel(
            power_rect,
            PANEL,
            ACCENT
        )

        draw_text(
            "ЭНЕРГОБЛОК СТАНЦИИ",
            WIDTH // 2,
            165,
            BIG,
            ACCENT,
            True
        )

        draw_text(
            "СИСТЕМА ПИТАНИЯ",
            WIDTH // 2,
            215,
            SMALL,
            MUTED,
            True
        )

        draw_text(
            "Основной контур: НЕАКТИВЕН",
            210,
            270,
            FONT,
            TEXT
        )

        draw_text(
            "Резервный контур: ДОСТУПЕН",
            210,
            315,
            FONT,
            TEXT
        )

        draw_text(
            "Состояние аккумуляторов: 37%",
            210,
            360,
            FONT,
            TEXT
        )

        draw_text(
            "Подключение резервного питания...",
            210,
            405,
            FONT,
            (0, 255, 0) #green
        )

        draw_text(
            "E — подключить",
            WIDTH // 2,
            470,
            SMALL,
            ACCENT,
            True
        )
        
    elif orbit_radio_open:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 110))
        SCREEN.blit(overlay, (0, 0))

        radio_rect = pygame.Rect(150, 120, 660, 400)

        draw_panel(
            radio_rect,
            PANEL,
            ACCENT
        )

        draw_text(
            "ПУЛЬТ СВЯЗИ",
            WIDTH // 2,
            165,
            BIG,
            ACCENT,
            True
        )

        draw_text(
            "ОРБИТАЛЬНЫЙ КАНАЛ СВЯЗИ",
            WIDTH // 2,
            215,
            SMALL,
            MUTED,
            True
        )

        draw_text(
            "Основной канал: НЕДОСТУПЕН",
            210,
            270,
            FONT,
            TEXT
        )

        draw_text(
            "Резервный канал: ГОТОВ",
            210,
            315,
            FONT,
            TEXT
        )

        draw_text(
            "Наземная станция: СИГНАЛ НЕ ПОЛУЧЕН",
            210,
            360,
            FONT,
            TEXT
        )

        draw_text(
            "Поиск аварийного канала...",
            210,
            405,
            FONT,
            ACCENT
        )

        draw_text(
            "E — установить связь",
            WIDTH // 2,
            470,
            SMALL,
            ACCENT,
            True
        )
        
    elif orbit_core_open:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 110))
        SCREEN.blit(overlay, (0, 0))

        core_rect = pygame.Rect(130, 100, 700, 440)

        draw_panel(
            core_rect,
            PANEL,
            ACCENT
        )

        draw_text(
            "ЦЕНТРАЛЬНЫЙ МОДУЛЬ",
            WIDTH // 2,
            145,
            BIG,
            ACCENT,
            True
        )

        draw_text(
            "СИСТЕМА УПРАВЛЕНИЯ СТАНЦИЕЙ",
            WIDTH // 2,
            195,
            SMALL,
            MUTED,
            True
        )

        draw_text(
            "Питание: ВОССТАНОВЛЕНО",
            190,
            250,
            FONT,
            (0, 255, 0)
        )

        draw_text(
            "Связь: РЕЗЕРВНЫЙ КАНАЛ",
            190,
            295,
            FONT,
            (255, 0, 0)
        )

        draw_text(
            "Навигация: ДОСТУПНА",
            190,
            340,
            FONT,
            (0, 255, 0) #green
        )

        draw_text(
            "Станция: АВАРИЙНЫЙ РЕЖИМ",
            190,
            385,
            FONT,
            (255, 255, 0)   # yellow
        )

        draw_text(
            "Все основные системы доступны.",
            190,
            430,
            FONT,
            (0, 255, 0) #green
        )

        draw_text(
            "E — продолжить",
            WIDTH // 2,
            495,
            SMALL,
            ACCENT,
            True
        )
        
    if orbit_final:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        SCREEN.blit(overlay, (0, 0))

        final_rect = pygame.Rect(120, 100, 720, 440)

        draw_panel(
            final_rect,
            PANEL,
            ACCENT
        )

        draw_text(
            "СТАНЦИЯ ВОССТАНОВЛЕНА",
            WIDTH // 2,
            155,
            BIG,
            (0, 255, 0),
            True
        )

        draw_text(
            "ЦЕНТРАЛЬНЫЙ МОДУЛЬ АКТИВИРОВАН",
            WIDTH // 2,
            205,
            SMALL,
            (0, 255, 0),
            True
        )

        draw_text(
            "Питание: НОРМА",
            200,
            270,
            FONT,
            (0, 255, 0)
        )

        draw_text(
            "Связь: ВОССТАНОВЛЕНА",
            200,
            315,
            FONT,
            (0, 255, 0),
        )

        draw_text(
            "Навигация: АКТИВНА",
            200,
            360,
            FONT,
            (0, 255, 0),
        )

        draw_text(
            "Станция снова доступна для работы.",
            200,
            415,
            FONT,
            (0, 255, 0),
        )

        draw_text(
            "E — завершить",
            WIDTH // 2,
            485,
            SMALL,
            ACCENT,
            True
        )
    
# Картинки главы 5
orbit_station_bg = load_image(
    "assets/orbit/station.png",
    (WIDTH, HEIGHT)
)

orbit_sprites = {
    "terminal": load_image("assets/orbit/terminal.png"),
    "power": load_image("assets/orbit/power.png"),
    "radio": load_image("assets/orbit/radio.png"),
    "core": load_image("assets/orbit/core.png"),
}
    
def update_chapter5():
    global vanya_frame_idx
    global vanya_current_dir
    global vanya_last_dir
    global vanya_last_anim_time

    keys = pygame.key.get_pressed()

    dx = (
        int(keys[pygame.K_d] or keys[pygame.K_RIGHT])
        - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
    )

    dy = (
        int(keys[pygame.K_s] or keys[pygame.K_DOWN])
        - int(keys[pygame.K_w] or keys[pygame.K_UP])
    )

    # Направление Вани
    if dx > 0 and dy > 0:
        vanya_current_dir = "down_right"
    elif dx > 0 and dy < 0:
        vanya_current_dir = "up_right"
    elif dx > 0:
        vanya_current_dir = "right"
    elif dx < 0 and dy > 0:
        vanya_current_dir = "down_right"
    elif dx < 0 and dy < 0:
        vanya_current_dir = "up_right"
    elif dx < 0:
        vanya_current_dir = "right"
    elif dy > 0:
        vanya_current_dir = "down"
    elif dy < 0:
        vanya_current_dir = "up"

    # Анимация
    if dx or dy:
        now = pygame.time.get_ticks()

        if now - vanya_last_anim_time >= 90:
            frames = vanya_movement_frames.get(
                vanya_current_dir,
                []
            )

            if frames:
                vanya_frame_idx = (
                    vanya_frame_idx + 1
                ) % len(frames)

            vanya_last_anim_time = now
    else:
        vanya_frame_idx = 0


    chapter5_speed = player_speed * 0.65
    # Скорость
    if dx and dy:
        speed = chapter5_speed / math.sqrt(2)
    else:
        speed = chapter5_speed
        

    # -------------------------------------------------
    # ДВИЖЕНИЕ ПО X
    # -------------------------------------------------

    player.x += int(dx * speed)

    for wall in orbit_walls:
        if player.colliderect(wall):
            if dx > 0:
                player.right = wall.left
            elif dx < 0:
                player.left = wall.right

    # -------------------------------------------------
    # ДВИЖЕНИЕ ПО Y
    # -------------------------------------------------

    player.y += int(dy * speed)

    for wall in orbit_walls:
        if player.colliderect(wall):
            if dy > 0:
                player.bottom = wall.top
            elif dy < 0:
                player.top = wall.bottom

    # Границы станции
    player.clamp_ip(
        pygame.Rect(
            140,
            170,
            660,
            290
        )
    )
    
    global near_orbit_object

    near_orbit_object = None

    for obj in orbit_objects:
        if player.inflate(35, 35).colliderect(obj["rect"]):
            near_orbit_object = obj
            break

# ---------------------------------------------------------
# MENU
# ---------------------------------------------------------
menu_buttons = [
    (pygame.Rect(320, 220, 320, 55), "Новая игра"),
    (pygame.Rect(320, 290, 320, 55), "Продолжить"),
    (pygame.Rect(320, 360, 320, 55), "Выход"),
]

def draw_menu():
    SCREEN.fill((8, 12, 19))
    draw_text("СПУТНИКС", WIDTH // 2, 105, HUGE, ACCENT, True)
    draw_text("ОБЛАКО АТАКУЕТ", WIDTH // 2, 155, FONT, CYAN, True)

    for rect, label in menu_buttons:
        button(rect, label)

    draw_text("Научное приключение • лаборатория • экспедиции • спутники",
              WIDTH // 2, 475, SMALL, MUTED, True)

def new_game():
    global prologue_qte_key_idx
    global qte_step_idx
    global qte_current_clicks
    global qte_timer
    global qte_active
    global prologue_qte_active
    global dialogue_index
    global prologue_step
    global ending_finished

    # QTE
    prologue_qte_key_idx = 0
    qte_step_idx = 0
    qte_current_clicks = 0
    qte_timer = 120
    qte_active = False
    prologue_qte_active = False

    # Диалоги
    dialogue_index = 0
    
    state.update({
        "chapter": 0,
        "scene": "prologue",
        "resume_scene": "prologue",
        "samples": 0,
        "choice": None,
        "discovered": [],
        "chapter1_progress": 0,
        "chapter2_progress": 0,
        "chapter3_progress": 0,
        "chapter4_progress": 0,
        "chapter5_progress": 0,
    })
    prologue_step = 0
    prologue_qte_active = False
    ending_finished = False
    save_game()

def continue_game():
    global selected_traps
    
    if not load_game():
        new_game()
        return

    scene = state.get("resume_scene", state.get("scene", "menu"))

    state["scene"] = scene

    if scene == "lab":
        reset_player()

    elif scene == "chapter1":
        start_chapter1(reset_progress=False)

    elif scene == "chapter2":
        selected_traps = []
        count = max(0, min(4, state.get("chapter2_progress", 0)))

        for i in range(count):
            selected_traps.append(i)

    elif scene == "chapter3":
        radio_order.clear()
        count = max(0, min(4, state.get("chapter3_progress", 0)))

        for i in range(count):
            radio_order.append(i)

    elif scene == "chapter4":
        ecosystem[:] = state.get(
            "ecosystem",
            [0, 0, 0, 0]
        )

    elif scene == "chapter5":
        start_chapter5(reset_progress=False)

    elif scene in dialogues:
        global dialogue_key, dialogue_index
        dialogue_key = scene
        dialogue_index = 0

# ---------------------------------------------------------
# DEBUG START
# ---------------------------------------------------------

if DEBUG_CHAPTER is not None:
    if DEBUG_CHAPTER == 1:
        state["chapter"] = 1
        state["scene"] = "chapter1"
        start_chapter1()

    elif DEBUG_CHAPTER == 2:
        state["chapter"] = 2
        state["scene"] = "chapter2"
        start_chapter2()

    elif DEBUG_CHAPTER == 3:
        state["chapter"] = 3
        state["scene"] = "chapter3"
        start_chapter3()

    elif DEBUG_CHAPTER == 4:
        state["chapter"] = 4
        state["scene"] = "chapter4"

        ecosystem[:] = [3, 2, 1, 2]

    elif DEBUG_CHAPTER == 5:
        state["chapter"] = 5
        state["scene"] = "chapter5"
        start_chapter5()

# ---------------------------------------------------------
# EVENTS & MAIN LOOP
# ---------------------------------------------------------
running = True

while running:
    CLOCK.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if inspecting_object:
                    inspecting_object = None
                    continue

                current_scene = state["scene"]

                # Если выходим из QTE — возвращаемся прямо перед ним
                if current_scene == "chapter1_boss":
                    state["scene"] = "chapter1"
                    qte_active = False

                elif current_scene == "chapter2_qte":
                    state["scene"] = "chapter2"
                    qte_active = False

                elif current_scene == "chapter3_qte":
                    state["scene"] = "chapter3"
                    qte_active = False

                elif current_scene == "chapter4_qte":
                    state["scene"] = "chapter4"
                    qte_active = False

                else:
                    # Обычный выход — запоминаем текущее место
                    state["resume_scene"] = current_scene
                    state["scene"] = "menu"

                save_game()
                continue
            
            scene = state["scene"]

            if inspecting_object:
                frames = lab_sprites.get(
                    inspecting_object["id"], []
                )
                
                if event.key == pygame.K_e:
                    if inspecting_object["id"] == "microscope" and microscope_stage == 0:
                        microscope_stage = 1
                        inspect_frame_index = 2
                        inspect_blink_until = pygame.time.get_ticks() + 115
                    continue

                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    inspect_frame_index = max(
                        1, inspect_frame_index - 1
                    )
                    blink_alpha = 255
                    blink_start_time = pygame.time.get_ticks()

                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    inspect_frame_index = min(
                        len(frames) - 1,
                        inspect_frame_index + 1
                    )
                    blink_alpha = 255
                    blink_start_time = pygame.time.get_ticks()

                continue

            if scene == "prologue":
                if prologue_qte_active:
                    handle_prologue_qte(event.key)
                elif event.key == pygame.K_SPACE:
                    advance_prologue()

            elif scene in dialogues and event.key == pygame.K_SPACE:
                advance_dialogue()

            elif scene == "lab" and event.key == pygame.K_e:
                interact_lab()

            elif scene == "chapter1":
                if event.key == pygame.K_e:
                    collect_sample()
                if event.key == pygame.K_SPACE and len(rover_samples) >= chapter1_samples_needed:
                    state["scene"] = "chapter1_boss"
                    start_qte()

            elif scene == "chapter1_boss":
                handle_qte_key(event.key)

            elif scene == "chapter2":
                if event.key == pygame.K_SPACE and len(selected_traps) == 4:
                    state["chapter"] = 2
                    state["scene"] = "chapter2_qte"
                    start_qte("hold")

            elif scene == "chapter2_qte":
                handle_qte_key(event.key)

            elif scene == "chapter3":
                if event.key == pygame.K_SPACE and len(radio_order) == 4:
                    state["chapter"] = 3
                    state["scene"] = "chapter3_qte"
                    start_qte("signal")

            elif scene == "chapter3_qte":
                handle_signal_qte(event.key)

            elif scene == "chapter4":
                if event.key == pygame.K_SPACE and ecosystem == [3, 2, 1, 2]:
                    state["chapter"] = 4
                    state["scene"] = "chapter4_qte"
                    start_qte("balance")

            elif scene == "chapter4_qte":
                handle_balance_qte(event.key)
                
            elif scene == "ending":
                if event.key == pygame.K_SPACE and ending_finished:
                    state["scene"] = "menu"
                    save_game()

            elif scene == "chapter5":
                if event.key == pygame.K_e:
                    
                    if orbit_final:
                        state["scene"] = "ending"
                        ending_frame = 0
                        ending_last_update = pygame.time.get_ticks()

                    # Если терминал уже открыт — закрываем его
                    elif orbit_terminal_open:
                        orbit_terminal_open = False

                        obj = next(
                            (obj for obj in orbit_objects if obj["type"] == "terminal"),
                            None
                        )

                        if obj and obj["step"] == orbit_step and not obj["used"]:
                            obj["used"] = True
                            orbit_step += 1
                            state["chapter5_progress"] = orbit_step
                            save_game()

                    elif orbit_power_open:
                        orbit_power_open = False

                        obj = next(
                            (obj for obj in orbit_objects if obj["type"] == "power"),
                            None
                        )

                        if obj and obj["step"] == orbit_step and not obj["used"]:
                            obj["used"] = True
                            orbit_step += 1
                            state["chapter5_progress"] = orbit_step
                            save_game()
                            
                    elif orbit_radio_open:
                        orbit_radio_open = False

                        obj = next(
                            (obj for obj in orbit_objects if obj["type"] == "radio"),
                            None
                        )

                        if obj and obj["step"] == orbit_step and not obj["used"]:
                            obj["used"] = True
                            orbit_step += 1
                            state["chapter5_progress"] = orbit_step
                            save_game()
                            
                    elif orbit_core_open:
                        orbit_core_open = False

                        obj = next(
                            (obj for obj in orbit_objects if obj["type"] == "core"),
                            None
                        )

                        if obj and obj["step"] == orbit_step and not obj["used"]:
                            obj["used"] = True
                            orbit_step += 1
                            state["chapter5_progress"] = orbit_step
                            save_game()
                            
                            orbit_final = True
                    
                    # Если терминал не открыт — взаимодействуем с объектом
                    elif near_orbit_object:
                        obj = near_orbit_object

                        if obj["step"] == orbit_step and not obj["used"]:

                            if obj["type"] == "terminal":
                                orbit_terminal_open = True

                            elif obj["type"] == "power":
                                orbit_power_open = True
                            
                            elif obj["type"] == "radio":
                                orbit_radio_open = True
                                
                            elif obj["type"] == "core":
                                orbit_core_open = True

                            else:
                                obj["used"] = True
                                orbit_step += 1
                                state["chapter5_progress"] = orbit_step
                                save_game()
                    

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            scene = state["scene"]

            if inspecting_object:
                inspecting_object = None
                continue

            if scene == "menu":
                if menu_buttons[0][0].collidepoint(pos):
                    new_game()
                elif menu_buttons[1][0].collidepoint(pos):
                    continue_game()
                elif menu_buttons[2][0].collidepoint(pos):
                    running = False

            elif scene == "chapter0_choice":
                handle_chapter0_choice(pos)

            elif scene == "chapter2":
                click_chapter2(pos)

            elif scene == "chapter3":
                click_chapter3(pos)

            elif scene == "chapter4":
                click_chapter4(pos)


    # -----------------------------------------------------
    # UPDATE
    # -----------------------------------------------------
    scene = state["scene"]

    if scene == "lab" and not inspecting_object:
        update_exploration()
        
    if scene == "chapter5":
        update_chapter5()
    
    if qte_active:
        
        # QTE для Chapter 4
        if qte_mode == "balance":
            balance_wave_time += 1

            # Волна постоянно толкает баланс
            if balance_wave == 1:
                balance_position -= balance_speed

            elif balance_wave == 2:
                balance_position += balance_speed

            elif balance_wave == 3:
                balance_position -= balance_speed * 1.4

            elif balance_wave == 4:
                balance_position += balance_speed * 1.4

            # Проверяем, находится ли индикатор в безопасной зоне
            if abs(balance_position) > balance_zone_width:
                qte_timer -= 2
            else:
                qte_timer = min(120, qte_timer + 1)

            # Следующая волна
            if balance_wave_time >= balance_wave_duration:
                balance_wave += 1
                balance_wave_time = 0

                if balance_wave == 2:
                    balance_zone_width = 0.30
                    balance_speed = 0.013

                elif balance_wave == 3:
                    balance_zone_width = 0.30
                    balance_speed = 0.012
                    balance_wave_duration = 240

                elif balance_wave == 4:
                    balance_zone_width = 0.27
                    balance_speed = 0.013
                    balance_wave_duration = 290

                elif balance_wave > 4:
                    qte_active = False
                    advance_after_qte()

            # Если баланс потерян слишком сильно
            if qte_timer <= 0:
                qte_active = False
                state["scene"] = "chapter4"
                save_game()
                
        # QTE for Chapter 2
        elif qte_mode == "hold":
            keys = pygame.key.get_pressed()

            if keys[qte_hold_key]:
                qte_hold_progress += 1
            else:
                qte_hold_progress = max(0, qte_hold_progress - 2)

            if qte_hold_progress >= qte_hold_required:
                qte_active = False
                advance_after_qte()

        else:
            qte_timer -= 1

            if qte_timer <= 0:
                qte_active = False

                current_scene = state["scene"]

                if current_scene == "chapter1_boss":
                    state["scene"] = "chapter1"
                elif current_scene == "chapter2_qte":
                    state["scene"] = "chapter2"
                elif current_scene == "chapter3_qte":
                    state["scene"] = "chapter3"
                elif current_scene == "chapter4_qte":
                    state["scene"] = "chapter4"

                save_game()

    elif scene == "chapter1":
        move_rover()
        if len(rover_samples) >= chapter1_samples_needed:
            for crack in crack_zones:
                if rover.colliderect(crack):
                    start_qte()
                    state["scene"] = "chapter1_boss"
                    break

    # -----------------------------------------------------
    # DRAW
    # -----------------------------------------------------
    scene = state["scene"]

    if scene == "menu":
        draw_menu()

    elif scene == "prologue":
        draw_prologue()

    elif scene == "lab":
        draw_lab()
        if inspecting_object:
            draw_inspect_screen()

    elif scene in dialogues:
        draw_dialogue()

    elif scene == "chapter0_choice":
        draw_choice(
            "Как поступить команде?",
            [
                "Проверить маршруты и продолжить исследование",
                "Сначала усилить связь со спутниками",
            ],
        )

    elif scene == "chapter1":
        draw_chapter1()

    elif scene == "chapter1_boss":
        draw_chapter1()
        draw_qte()

    elif scene == "chapter2":
        draw_chapter2()

    elif scene == "chapter2_qte":
        SCREEN.fill((20, 18, 14))

        draw_text(
            "БОСС: РОЙ",
            WIDTH // 2,
            100,
            HUGE,
            YELLOW,
            True
        )

        draw_text(
            "Ветер меняется. Рой разворачивается к Роверу.",
            WIDTH // 2,
            145,
            FONT,
            TEXT,
            True
        )

        draw_hold_qte()

    elif scene == "chapter3":
        draw_chapter3()

    elif scene == "chapter3_qte":
        SCREEN.fill((12, 15, 25))

        draw_text(
            "БОСС: РАДИОПОМЕХА",
            WIDTH // 2,
            70,
            HUGE,
            RED,
            True
        )

        draw_text(
            "Стабилизируйте канал связи с Ровером",
            WIDTH // 2,
            115,
            FONT,
            TEXT,
            True
        )

        draw_signal_qte()

    elif scene == "chapter4":
        draw_chapter4()

    elif scene == "chapter4_qte":
        SCREEN.fill((10, 18, 20))

        draw_text(
            "БОСС: НЕСТАБИЛЬНАЯ ЭКОСИСТЕМА",
            WIDTH // 2,
            70,
            HUGE,
            ACCENT,
            True
        )

        draw_balance_qte()

    elif scene == "chapter5":
        draw_chapter5()

    elif scene == "ending":
        draw_ending_video()

        if ending_finished:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((5, 10, 18, 190))
            SCREEN.blit(overlay, (0, 0))

            draw_text(
                "ЭКСПЕРИМЕНТ ЗАВЕРШЁН",
                WIDTH // 2,
                250,
                HUGE,
                GREEN,
                True
            )

            draw_text(
                "Данные с орбитальной станции получены.",
                WIDTH // 2,
                320,
                FONT,
                WHITE,
                True
            )

            draw_text(
                "SPACE — вернуться в главное меню",
                WIDTH // 2,
                420,
                SMALL,
                MUTED,
                True
            )

    
    pygame.display.flip()

pygame.quit()