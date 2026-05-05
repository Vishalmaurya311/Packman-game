from random import choice
from turtle import *
from freegames import floor, vector
import math

# ---------------------- STATE ----------------------
state = {
    'score': 0,
    'name': '',
    'game_over': False,
    'level': 1,
    'lives': 3,
    'paused': False
}

path = Turtle(visible=False)
writer = Turtle(visible=False)

aim = vector(5, 0)
pacman = vector(-40, -80)

ghosts = [
    [vector(-180, 160), vector(5, 0)],
    [vector(-180, -160), vector(0, 5)],
    [vector(100, 160), vector(0, -5)],
    [vector(100, -160), vector(-5, 0)],
]

# ---------------------- MAP ----------------------
def get_tiles():
    return [
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,0,0,0,
        0,1,0,0,1,0,0,1,0,1,0,0,1,0,0,1,0,0,0,0,
        0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,
        0,1,0,0,1,0,1,0,0,0,1,0,1,0,0,1,0,0,0,0,
        0,1,1,1,1,0,1,1,0,1,1,0,1,1,1,1,0,0,0,0,
        0,1,0,0,1,0,0,1,0,1,0,0,1,0,0,0,0,0,0,0,
        0,1,0,0,1,0,1,1,1,1,1,0,1,0,0,0,0,0,0,0,
        0,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,0,0,0,0,
        0,0,0,0,1,0,1,1,1,1,1,0,1,0,0,1,0,0,0,0,
        0,0,0,0,1,0,1,0,0,0,1,0,1,0,0,1,0,0,0,0,
        0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,0,0,0,
        0,1,0,0,1,0,0,1,0,1,0,0,0,0,0,1,0,0,0,0,
        0,1,1,0,1,1,1,1,1,1,1,1,1,0,1,1,0,0,0,0,
        0,0,1,0,1,0,1,0,0,0,1,0,1,0,1,0,0,0,0,0,
        0,1,1,1,1,0,1,1,0,1,1,0,1,1,1,1,0,0,0,0,
        0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,1,0,0,0,0,
        0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    ]

tiles = get_tiles()

# ---------------------- HELPERS ----------------------
def offset(point):
    x = (floor(point.x, 20) + 200) / 20
    y = (180 - floor(point.y, 20)) / 20
    return int(x + y * 20)

def valid(point):
    i = offset(point)
    if tiles[i] == 0:
        return False
    i = offset(point + vector(19, 19))
    if tiles[i] == 0:
        return False
    return point.x % 20 == 0 or point.y % 20 == 0

# ---------------------- HUD (COLORED BAR) ----------------------
def draw_hud():
    writer.clear()

    # background bar
    path.up()
    path.goto(-210, 205)
    path.color("darkblue")
    path.down()

    for _ in range(2):
        path.begin_fill()
        for _ in range(2):
            path.forward(420)
            path.right(90)
            path.forward(25)
            path.right(90)
        path.end_fill()

    # text
    writer.up()
    writer.goto(0, 210)
    writer.color("white")

    hearts = "❤️" * state['lives']

    writer.write(
        f"{state['name']}   Score: {state['score']}   Level: {state['level']}   Lives: {hearts}",
        align="center",
        font=("Arial", 11, "bold")
    )

# ---------------------- WORLD ----------------------
def world():
    bgcolor('black')
    path.color('blue')

    for i, tile in enumerate(tiles):
        if tile > 0:
            x = (i % 20) * 20 - 200
            y = 180 - (i // 20) * 20

            path.up()
            path.goto(x, y)
            path.down()

            for _ in range(4):
                path.forward(20)
                path.left(90)

            if tile == 1:
                path.up()
                path.goto(x + 10, y + 10)
                path.dot(2, 'white')

# ---------------------- RESTART ----------------------
def restart():
    global pacman, aim, ghosts, tiles

    state['score'] = 0
    state['game_over'] = False
    state['level'] = 1
    state['lives'] = 3
    state['paused'] = False

    pacman = vector(-40, -80)
    aim = vector(5, 0)

    ghosts = [
        [vector(-180, 160), vector(5, 0)],
        [vector(-180, -160), vector(0, 5)],
        [vector(100, 160), vector(0, -5)],
        [vector(100, -160), vector(-5, 0)],
    ]

    tiles = get_tiles()

    clear()
    world()
    draw_hud()

    ontimer(move, 100)

# ---------------------- GHOST AI (SMOOTH CHASE) ----------------------
def chase_ghost(ghost, target):
    gx, gy = ghost.x, ghost.y
    px, py = target.x, target.y

    dx = px - gx
    dy = py - gy

    if abs(dx) > abs(dy):
        step = vector(5 if dx > 0 else -5, 0)
    else:
        step = vector(0, 5 if dy > 0 else -5)

    if valid(ghost + step):
        return step
    return choice([vector(5,0), vector(-5,0), vector(0,5), vector(0,-5)])

# ---------------------- GAME LOOP ----------------------
def move():
    if state['game_over'] or state['paused']:
        return

    draw_hud()
    clear()

    # move pacman
    if valid(pacman + aim):
        pacman.move(aim)

    i = offset(pacman)

    # eat dot
    if tiles[i] == 1:
        tiles[i] = 2
        state['score'] += 1

    # level complete
    if 1 not in tiles:
        state['level'] += 1
        writer.clear()
        writer.goto(0, 0)
        writer.color("white")
        writer.write(f"LEVEL {state['level']} COMPLETE!",
                     align="center", font=("Arial", 20, "bold"))
        ontimer(restart, 1500)
        return

    # draw pacman
    up()
    goto(pacman.x + 10, pacman.y + 10)
    dot(20, 'yellow')

    # ghosts
    for ghost, _ in ghosts:
        step = chase_ghost(ghost, pacman)
        if valid(ghost + step):
            ghost.move(step)

        up()
        goto(ghost.x + 10, ghost.y + 10)
        dot(20, 'red')

    update()

    # collision
    for ghost, _ in ghosts:
        if abs(pacman - ghost) < 20:
            state['lives'] -= 1

            if state['lives'] == 0:
                state['game_over'] = True
                writer.goto(0, 20)
                writer.color("white")
                writer.write("GAME OVER 💀",
                             align="center", font=("Arial", 24, "bold"))
                writer.goto(0, -20)
                writer.write("Press R to Restart",
                             align="center", font=("Arial", 14, "normal"))
                return
            else:
                pacman.x, pacman.y = -40, -80

    ontimer(move, 80)

# ---------------------- CONTROL ----------------------
def change(x, y):
    if not state['paused'] and valid(pacman + vector(x, y)):
        aim.x = x
        aim.y = y

def toggle_pause():
    state['paused'] = not state['paused']
    if not state['paused']:
        move()

# ---------------------- SETUP ----------------------
def setup_game():
    state['name'] = textinput("Player Name", "Enter your name:") or "Player"

    setup(420, 420, 370, 0)
    hideturtle()
    tracer(False)

    listen()
    onkey(lambda: change(5, 0), 'Right')
    onkey(lambda: change(-5, 0), 'Left')
    onkey(lambda: change(0, 5), 'Up')
    onkey(lambda: change(0, -5), 'Down')

    onkey(restart, 'r')
    onkey(toggle_pause, 'p')

    world()
    draw_hud()
    move()
    done()

setup_game()