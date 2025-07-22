"""
DAN'S DUNGEON GAME LOGIC
"""

from pydantic import BaseModel
from typing import Callable
from moves import Move      #import the move class
import random

from levels import Level                                    #import Level class
from levels import LEVELS, SECRET_LEVELS, level_test        #import the levels themselves

from pygame import mixer
mixer.init()
mixer.music.load("music/dungeon_music_1.mp3")
mixer.music.play(loops = -1)

REVERSE = {'left':'right', 'right':'left', 'up':'down', 'down':'up'}

class DungeonGame(BaseModel):
    status: str = "running"
    player_state: str = 'normal'
    armor_worn: bool = False
    armor_health: int = 3
    player_speed: int = 15
    current_level: Level
    level_number: int = 0
    secret_level_number: int = 0
    x: int
    y: int
    moves: list[Move] = []
    coins: int = 0
    health: int = 5
    items: list[str] = []
    hurt_counter: int = 0

def move_player(game, direction: str) -> None:
    # initialize move
    move = None
    
    # WASD movement
    new_x, new_y = get_next_position(game.x, game.y, direction)
    if (new_x - game.x) == 0 and (new_y - game.y) == 0:
        return
    elif game.current_level.level[new_y][new_x] in "t$wshk.D":
        if game.armor_worn == True:
            tile = 'deep_elf_knight_new'
        else:
            tile = 'player'
        move = Move(tile = tile,
                    from_x=game.x,
                    from_y=game.y,
                    speed_x = (new_x - game.x) * 15,
                    speed_y = (new_y - game.y) * 15,
                    callback = player_move_finished
                    )
    #print('x: ' + str(new_x), 'y: ' + str(new_y))
    
    # variable for next tile
    next_tile = game.current_level.level[new_y][new_x]

    # pick up coins
    if next_tile == "$":
        game.current_level.set_tile(x = new_x, y = new_y, character = ".")
        game.coins += 1

    # trigger trap
    if next_tile == "t":
        game.current_level.set_tile(x = new_x, y = new_y, character = ".")
        move.finished = take_damage

     # trigger healing potion
    if next_tile == "h":
        game.current_level.set_tile(x = new_x, y = new_y, character = ".")
        move.finished = heal
    
    # check for key
    if next_tile == "k":
        game.items.append("key")
        game.current_level.set_tile(x = new_x, y = new_y, character = ".")

    # open door if there and if key in inventory
    if "key" in game.items and next_tile == "d":
        game.items.remove("key")
        game.current_level.set_tile(x = new_x, y = new_y, character = "D")

    # check for chest and add item if there
    for c in game.current_level.chests:
        chest_position = [c.x, c.y]
        if [new_x, new_y] == chest_position and c.opened == False:
            if c.contents == 'armor':
                if game.armor_worn == True:
                    game.armor_health = 3
                else:
                    game.armor_worn = True
            else:
                game.items.append(c.contents)
            c.opened = True
    
    # check if armor has been removed
    if game.armor_worn == False:
        if 'armor' in game.items:
            game.items.remove('armor')
            game.armor_health = 3
    
    # check for tiles that can be walked through
    if game.current_level.level[new_y][new_x] in ".Dws":
        game.x = new_x
        game.y = new_y
        if move:                
            game.moves.append(move)

    # teleporter
    check_teleporters(game)

    # check for stairs
    if game.current_level.level[new_y][new_x] == "x":
        game.level_number += 1
        if game.level_number < len(LEVELS):
            game.current_level = LEVELS[game.level_number]
            game.x = game.current_level.spawn[0]
            game.y = game.current_level.spawn[1]
        else:
            game.status = "finished"
            mixer.music.stop()
    elif game.current_level.level[new_y][new_x] == "y":
        game.secret_level_number += 1
        if game.secret_level_number < len(SECRET_LEVELS):
            game.current_level = SECRET_LEVELS[game.secret_level_number]
            game.x = game.current_level.spawn[0]
            game.y = game.current_level.spawn[1]

    # open secret door 
    for s in game.current_level.switches:
        if game.x == s.x and game.y == s.y:
            if game.current_level.level[s.door_y][s.door_x] == "#":
                game.current_level.level[s.door_y][s.door_x] = "y"
                move = Move(tile="wall", 
                        from_x = s.door_x, from_y = s.door_y, 
                        speed_x = 0, speed_y = 2
                    )
                game.moves.append(move)
    
    # check for collision
    check_collision(game)
    check_collision_monster(game)

def player_move_finished(game):
    #outputs the coordinates of the player
    print(game.x, game.y)

def start_game():
    current_level = LEVELS[0]
    #current_level = level_test
    return DungeonGame(
        current_level=current_level,
        x=current_level.spawn[0],
        y=current_level.spawn[1],
        #level = level_one
    )

# take damage - monster
def take_damage_monster(game, monster):
    if game.armor_worn == True and game.hurt_counter <= 0:
        if monster.type == 'skeleton':
            game.armor_health -= 1
        elif monster.type == 'giant':
            game.armor_health = 0
        if game.armor_health == 0:
            game.armor_worn = False
    elif game.hurt_counter <= 0:
        if monster.type == 'skeleton':
            game.health -= 1
        elif monster.type == 'giant':
            game.health = 0
        elif monster.type == 'rat' and game.coins > 0:
            game.coins -= 1
        elif monster.type == 'spider':
            game.health -= 1
            game.player_state = 'poison'
    if game.health <= 0:
        game.status = "game over"
    if game.hurt_counter <= 0:
        game.hurt_counter = 100

# take damage - fireball and traps
def take_damage(game):
    if game.armor_worn == True and game.hurt_counter <= 0:
        game.armor_health -= 1
        if game.armor_health <= 0:
            game.armor_worn = False
        if game.hurt_counter <= 0:
            game.hurt_counter = 100
    else:
        if game.hurt_counter <= 0:
            game.health -= 1
        if game.health <= 0:
            game.status = 'game over'
        if game.hurt_counter <= 0:
            game.hurt_counter = 100

# heal
def heal(game):
    if game.health < 5:
        game.health += 1
        if game.player_state == 'poison':
            game.player_state = 'normal'

# restore entire health 
def restore(game):
    if game.health < 3:
        game.health = 3

# teleporters
def check_teleporters(game):
    for t in game.current_level.teleporters:
        if game.x == t.x and game.y == t.y:
            game.x = t.target_x
            game.y = t.target_y

# movement
def get_next_position(x, y, direction):
    new_x = x
    new_y = y
    if direction == "right":
        new_x += 1
    elif direction == "left":
        new_x -= 1
    elif direction == "up":
        new_y -= 1
    elif direction == "down":
        new_y += 1
    return new_x, new_y

# fireball movement
def move_fireball(game, fireball):
    new_x, new_y = get_next_position(fireball.x, fireball.y, fireball.direction)
    if game.current_level.level[new_y][new_x] in "w.$ks":  # flies over coins and keys
        fireball.move = Move(
            tile = 'fireball',
            from_x = fireball.x, from_y = fireball.y, 
            speed_x = (new_x - fireball.x) * fireball.speed, speed_y = (new_y - fireball.y) * fireball.speed
        )
        game.moves.append(fireball.move)
        fireball.x = new_x
        fireball.y = new_y            
    else:
        fireball.direction = REVERSE[fireball.direction]

# monster movement
def move_monster(game, monster):
    monster.direction = random.choice(["up", "down", "left", "right"])
    new_x, new_y = get_next_position(monster.x, monster.y, monster.direction)
    if game.current_level.level[new_y][new_x] in "w.s$k":  # moves over coins and keys
        monster.move = Move(
            tile = monster.type, 
            from_x = monster.x, from_y = monster.y, 
            speed_x = (new_x - monster.x) * monster.speed, speed_y = (new_y - monster.y) * monster.speed
        )
        monster.x = new_x
        monster.y = new_y
        game.moves.append(monster.move)            
    else:
        monster.direction = REVERSE[monster.direction]

# update fireballs, monsters
def update(game):
    check_collision(game)
    check_collision_monster(game)
    for f in game.current_level.fireballs:
        if (f.move and f.move.complete) or (not f.move):
            move_fireball(game, f)
    for m in game.current_level.monsters:
        if (m.move and m.move.complete) or (not m.move):
            move_monster(game, m)         
    game.hurt_counter -= 1
    #print(game.hurt_counter)

# collision check for fireballs, monsters
def check_collision(game):
    for f in game.current_level.fireballs:
        if f.x == game.x and f.y == game.y and f.move.complete:
            take_damage(game)

def check_collision_monster(game):
    for m in game.current_level.monsters:
        if m.x == game.x and m.y == game.y and m.move.complete:
            take_damage_monster(game, m)
            #print('take damage')