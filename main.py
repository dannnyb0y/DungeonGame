"""
graphics engine for 2D games
"""
import os
import time
import numpy as np
import cv2
from game import start_game, move_player, update
from cutscene import show_titlescreen, show_gameover, game_complete
from levels import LEVELS

TILE_PATH = os.path.split(__file__)[0] + '/tiles'
MUSIC_PATH = os.path.split(__file__)[0] + '/music'

message = ''
msg_delay = 0

def create_message(text: str):
    global message 
    global msg_delay
    message = text
    msg_delay = 100

# title of the game window
GAME_TITLE = "Dungeon Explorer"

# map keyboard keys to move commands
MOVES = {
    "a": "left",
    "d": "right",
    "w": "up",
    "s": "down",
}

# controls are inverted when poisoned
MOVES_POISONED = {
    "a": "right",
    "d": "left",
    "w": "down",
    "s": "up",
}

#
# constants measured in pixels
#

TILE_SIZE = 64  

def get_level_size(game):
    xdim = len(game.current_level.level[0])
    ydim = len(game.current_level.level)
    return xdim, ydim

def read_image(filename: str) -> np.ndarray:
    """
    Reads an image from the given filename and doubles its size.
    If the image file does not exist, an error is created.
    """
    img = cv2.imread(filename)  # sometimes returns None
    if img is None:
        raise IOError(f"Image not found: '{filename}'")
    img = np.kron(img, np.ones((2, 2, 1), dtype=img.dtype))  # double image size
    return img

def read_images():
    return {
        filename[:-4]: read_image(os.path.join(TILE_PATH, filename))
        for filename in os.listdir(TILE_PATH)
        if filename.endswith(".png")
    }

def read_music():
    return {
        filename[:-4]: read_image(os.path.join(MUSIC_PATH, filename))
        for filename in os.listdir(MUSIC_PATH)
        if filename.endswith(".png")
    }

def draw_tile(frame, x, y, image, xbase=0, ybase=0):
    # calculate screen position in pixels
    xpos = xbase + x * TILE_SIZE
    ypos = ybase + y * TILE_SIZE
    #print(xpos,ypos)
    # copy the image to the screen
    frame[ypos : ypos + TILE_SIZE, xpos : xpos + TILE_SIZE] = image

def draw_move(frame, move, images):
    draw_tile(frame, x=move.from_x, y=move.from_y, image=images[move.tile], xbase=move.progress * move.speed_x, ybase=move.progress * move.speed_y)
    move.progress += 1

def clean_moves(game, moves):
    result = []
    for m in moves:
        if m.progress * max(abs(m.speed_x), abs(m.speed_y)) < TILE_SIZE:
            result.append(m)
        else:
            m.complete = True
            if m.finished is not None:
                m.finished(game)
    return result

def is_player_moving(moves):
    return any([m for m in moves if m.tile == "player" or m.tile == 'deep_elf_knight_new'])

def is_fireball_moving(fireball):
    if fireball.move == None or fireball.move.complete:
        return False
    else:
        return True

def is_monster_moving(monster):
    if monster.move == None or monster.move.complete:
        return False
    else:
        return True
    
# confirmation for saving and loading
def saveload_confirm(frame):
    global message, msg_delay
    if msg_delay > 0:
        cv2.putText(frame,
            str(message),
            org=((frame.shape[1] - TILE_SIZE * 2) + 10, 500),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.5,
            color=(255, 128, 128),
            thickness=1,
            ) 
    msg_delay -= 1

def draw(game, images, moves):
    # initialize screen
    xdim, ydim = get_level_size(game)
    SCREEN_SIZE_X, SCREEN_SIZE_Y = (xdim * TILE_SIZE)+128, ydim * TILE_SIZE
    #SCREEN_SIZE_X, SCREEN_SIZE_Y = 1920, 1080

    frame = np.zeros((SCREEN_SIZE_Y, SCREEN_SIZE_X, 3), np.uint8)

    # text and icon for coin counter
    if game.coins < 10:
        coin_text = SCREEN_SIZE_X - TILE_SIZE + 10
    else:
        coin_text = SCREEN_SIZE_X - TILE_SIZE
    cv2.putText(frame,
            str(game.coins),
            org=(coin_text, 110),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.5,
            color=(255, 128, 128),
            thickness=3,
            )
    draw_tile(frame, x=xdim, y=1, image=images["coin"])

    # draw health icon and text
    draw_tile(frame, x=xdim, y=0, image=images["heart"])
    cv2.putText(frame,
        str(game.health),
        org=(SCREEN_SIZE_X - TILE_SIZE + 10, 110-64),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=1.5,
        color=(255, 128, 128),
        thickness=3,
        )
    
    # draw level label
    cv2.putText(frame,
        str(game.current_level.title),
        org=((SCREEN_SIZE_X - TILE_SIZE * 2) + 7, 600),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=1,
        color=(255, 128, 128),
        thickness=2,
        )           

    # draw dungeon tiles
    symbols = {".": "floor",      # dictionary for symbols
               "#": "wall", 
               "f": "fountain", 
               "x": "stairs_down", 
               "y": "stairs_up",
               "$": "coin", 
               "t": "trap",
               "w": "water", 
               "k": "key", 
               "D": "open_door", 
               "d": "closed_door", 
               "h": "potion", 
               "c": "chest", 
               "s": "slime"}
    for y, row in enumerate(game.current_level.level):
        for x, tile in enumerate(row):
            draw_tile(frame, x=x, y=y, image=images[symbols[tile]])
    
    # draw teleporters
    for t in game.current_level.teleporters:
        draw_tile(frame, x=t.x, y=t.y, image=images["teleporter"])
    
    # draw chests
    for c in game.current_level.chests:
        if c.opened == False:
            draw_tile(frame, x=c.x, y=c.y, image=images["chest"])

    # draw armor
    if game.armor_worn == True:
        draw_tile(frame, x=xdim, y=2, image=images["armor"])
        cv2.putText(frame,
            str(game.armor_health),
            org=(SCREEN_SIZE_X - TILE_SIZE + 10, 110+64),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.5,
            color=(255, 128, 128),
            thickness=3,
            )

    # inventory
    for i, item in enumerate(game.items):
        y = i // 2
        x = i % 2
        draw_tile(frame, xbase=xdim * TILE_SIZE, ybase=ydim + (64 * 3), x=x, y=y, image=images[item])

    # draw player, fireball, monsters
    while game.moves:
        moves.append(game.moves.pop())
    if not is_player_moving(moves):
        if game.armor_worn == True:
            draw_tile(frame=frame, x=game.x, y=game.y, image=images["deep_elf_knight_new"])
        else:
            draw_tile(frame=frame, x=game.x, y=game.y, image=images["player"])
    for f in game.current_level.fireballs:
        if not is_fireball_moving(f):
            draw_tile(frame=frame, x=f.x, y=f.y, image=images["fireball"])
    for m in game.current_level.monsters:
        if not is_monster_moving(m):
            draw_tile(frame=frame, x=m.x, y=m.y, image=images[m.type])
    
    # draw everything that moves
    for m in moves:
        draw_move(frame=frame, move=m, images=images)

    # confirmation of save/load
    saveload_confirm(frame)

    # display complete image
    cv2.imshow(GAME_TITLE, frame)
    return frame


def handle_keyboard(game, frame):
    # map keys to commands
    from game import DungeonGame
    
    key = chr(cv2.waitKey(1) & 0xFF)
    if key == "q":
        game.status = "exited"
    
    # saving and loading
    if key == "p":
        save_time = time.asctime()
        file_name = "savegame.json"
        open(file_name, "w").write(game.model_dump_json())
        create_message('Game Saved')
    elif key == "o":
        file_name = "savegame.json"
        s = open(file_name, "r").read()
        game = DungeonGame.model_validate_json(s)
        create_message('Game Loaded')
    
    # cheat for level skipping
    elif key == "m":
        game.level_number += 1
        game.current_level = LEVELS[game.level_number]
    elif key == "n":
        game.level_number -= 1
        game.current_level = LEVELS[game.level_number]
      
    # poisoned
    if game.player_state == 'poison':
        return MOVES_POISONED.get(key), game
    else:
        return MOVES.get(key), game


def main():
    images = read_images()
    show_titlescreen()
    game = start_game()
    
    xdim, ydim, = get_level_size(game)

    queued_move = None
    moves = []
    counter = 0

    # video
    '''tick = time.time()
    xdim, ydim = get_level_size(game)
    SCREEN_SIZE_X_video, SCREEN_SIZE_Y_video = (xdim * TILE_SIZE)+128, ydim * TILE_SIZE
    fourcc = cv2.VideoWriter_fourcc(*"MP4V")
    out = cv2.VideoWriter('daniel.mp4', fourcc, 
                          60.0, 
                          (SCREEN_SIZE_X_video, SCREEN_SIZE_Y_video))'''

    while game.status == "running":
        #draw(game, images, moves)
        frame = draw(game, images, moves)
        update(game)
        moves = clean_moves(game, moves)
        queued_move, game = handle_keyboard(game, frame)
        if not is_player_moving(moves):
            move_player(game, queued_move)
        
        # video
        '''frame = draw(game, images, moves)
        out.write(frame)'''

    if game.status == "game over":
        show_gameover()
    elif game.status == "finished":
        game_complete()
    #elif game.status == "exited":
        #quit_game()

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
