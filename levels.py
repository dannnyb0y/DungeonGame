from pydantic import BaseModel
from typing import Callable
from moves import Move
import random

class Move(BaseModel):
    tile: str
    from_x: int
    from_y: int
    speed_x: int
    speed_y: int
    progress: int = 0
    complete: bool = False
    finished: Callable = None

class Teleporter(BaseModel):
    x: int
    y: int
    target_x: int
    target_y: int

class Switch(BaseModel):
    x: int
    y: int
    door_x: int
    door_y: int

class Fireball(BaseModel):
    x: int
    y: int
    direction: str
    move: Move = None
    speed: int

class Monster(BaseModel):
    type: str
    x: int
    y: int
    direction: str
    move: Move = None
    speed: int

class HealingPotion(BaseModel):
    x: int
    y: int

class Chest(BaseModel):
    x: int
    y: int
    contents: str
    opened: bool = False

class Armor(BaseModel):
    x: int
    y: int
    worn: bool = False

class Level(BaseModel):
    level: list[list[str]]
    title: str
    spawn: list[int]
    teleporters: list[Teleporter] = []
    switches: list[Switch] = []
    fireballs: list[Fireball] = []
    monsters: list[Monster] = []
    chests: list[Chest] = []

    def set_tile(self, x, y, character):
        self.level[y][x] = character


# turn level string into a list 
def parse_level(level):
    return [list(row) for row in level]

# level definitions
level_one = Level(level=parse_level([
        "##########",
        "#..$..$..#",
        "#........#",
        "#######..#",
        "#........#",
        "#.#$..$..#",
        "#.#......#",
        "#.########", 
        "#.......x#",
        "##########"
    ]), 
    title = "Level 1",
    spawn = [1, 1],
    )

level_two = Level(level=parse_level([
        "##########",
        "#...###.$#",
        "#.$..h...#",
        "#.$.##...#",
        "#.$.####.#",
        "#......#t#",
        "#wwww#.#.#",
        "#wffw#.#.#", 
        "#wwww#x#.#",
        "##########"
    ]),
    spawn = [8, 8],
    title = "Level 2", 
    monsters = [Monster(x=2, y=5, type = 'rat', speed = 1, direction = 'down')]
    )

level_three  = Level(level=parse_level([
        "##########",
        "#........#",
        "#...##.k.#",
        "##d###...#",
        "#...##...#",
        "#.h.##...#",
        "#...##...#",
        "#w.w####.#", 
        "#wxw##...#",
        "##########"
    ]),
    spawn = [6, 8],
    title = "Level 3", 
    fireballs = [
        Fireball(x=6, y=2, direction = "right", speed = 1),
        Fireball(x=8, y=5, direction = "left", speed = 1)
    ]
    )

level_four  = Level(level=parse_level([
        "##########",
        "#....h..x#",
        "#d########",
        "#........#",
        "#..$.....#",
        "#........#",
        "#....$...#",
        "##.#.....#", 
        "##.#.....#",
        "##########"
    ]),
    spawn = [2, 8],
    title = "Level 4",
    fireballs = [
        Fireball(x=8, y=3, direction = "down", speed = 2),
                ],
    monsters = [Monster(x=6, y=8, direction = 'right', type = 'skeleton', speed = 1), 
                 Monster(x=5, y = 5, direction = 'left', type = 'skeleton', speed = 1), 
                 Monster(x=8, y=3, direction = 'down', type = 'giant', speed = 1)
                ], 
    chests = [Chest(x=8, y=8, contents = 'key'), Chest(x=2, y=7, contents = 'armor')], 
    )

level_five = Level(level=parse_level([
        "##########",
        "#........#",
        "##########",
        "##.......#",
        "##.#.....#",
        "##.#.....#",
        "#x.#.....#",
        "#..#.....#", 
        "#........#",
        "##########"
    ]),
    spawn = [8, 1],
    title = "Level 5", 
    fireballs = [
        Fireball(x=4, y=3, direction = "down", speed = 5),
        Fireball(x=5, y=6, direction = "up", speed = 5)
                ],
    teleporters = [
        Teleporter(x = 1, y=1, target_x=8, target_y=8)
    ], 
    chests = [Chest(x = 2, y = 8, contents = 'armor')], 
    monsters = [Monster(x = 6, y = 4, direction = 'down', type = 'spider', speed = 3)]
    )

level_six = Level(level=parse_level([
        "##########",
        "#xwwwwwww#",
        "#wwwwwwww#",
        "#wwwwwwww#",
        "#wwwwwwww#",
        "###wwwwww#",
        "#wwwwwwww#",
        "###wwwwww#", 
        "#wwwwwwww#",
        "##########"
    ]),
    spawn = [1, 6],
    title = "Level 6", 
    chests = [Chest(x = 1, y=8, contents = 'potion')], 
    monsters = [Monster(x=1, y=1, type = 'giant', direction = 'down', speed = 1), 
                Monster(x = 5, y = 3, type = 'spider', direction = 'left', speed = 2)], 
    fireballs = [Fireball(x = 8, y=6, speed = 3, direction = 'left')]
    )

level_seven = Level(level=parse_level([
        "##########",
        "#ssssssss#",
        "#ssssssss#",
        "#ssssssss#",
        "#ssssssss#",
        "#ssssssss#",
        "#ssssssss#",
        "#ssssssss#", 
        "#ssssssss#",
        "##########"
    ]),
    spawn = [1, 1],
    title = "Level 6", 
    chests = [Chest(x = 1, y=8, contents = 'potion')], 
    monsters = [Monster(x=1, y=1, type = 'skeleton', direction = 'down', speed = 5), 
                Monster(x = 5, y = 3, type = 'snake', direction = 'left', speed = 2)], 
    fireballs = [Fireball(x = 8, y=6, speed = 3, direction = 'left')]
    )

LEVELS = [level_one, level_two, level_three, level_four, level_five, level_six, level_seven]

# secret level definitions

secret_level_one = Level(level=parse_level([
        "##########",
        "#........#",
        "#........#",
        "#........#",
        "#........#",
        "#........#",
        "#........#",
        "#........#", 
        "#........#",
        "##########"
    ]), 
    spawn = [1, 1], 
    title = "Level S1" 
    )

SECRET_LEVELS = [secret_level_one]

# testing
level_test = Level(level=parse_level([
        "#####",
        "#...#",
        "#...#",
        "#...#",
        "#.$.#",
        "#.$.#",
        "#####"
    ]), 
    title = "TESTING",
    spawn = [1, 1],
    monsters = [Monster(x=3, y=3, type = 'rat', speed = 3, direction = 'left')], 
    #fireballs = [Fireball(x=2, y=3, speed = 1, direction = 'up'), 
                 #Fireball(x=3, y=3, speed = 1, direction = 'up')]
    )