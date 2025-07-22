import cv2
import time

# title screen
def show_titlescreen():
    img = cv2.imread("title.png")
    img[-150:] = 0  # last 100 pixel rows are black
    img = cv2.putText(
        img,
        "Dan's Dungeon",
        org=(15, 1050),  # x/y position of the text
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=1,
        color=(255, 255, 255),  # white
        thickness=2,
    )
    img = cv2.putText(
        img,
        "Press 'L' Key for Tutorial",
        org=(1500, 1050),  # x/y position of the text
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=1,
        color=(255, 255, 255),  # white
        thickness=2,
    )
    centerText("Press Any Key to Begin", cv2.FONT_HERSHEY_SIMPLEX, 2, 2, (255, 255, 255), img, 0, 450)

    cv2.imshow("Cutscene", img)
    key = chr(cv2.waitKey(0) & 0xFF)
    if key == "l":
        cv2.destroyAllWindows()
        show_instructions()
    else:
        cv2.destroyAllWindows() # destroy window for game to be shown

def show_instructions():
    img = cv2.imread("gameover.png") # background image (black)
    centerText("Find the stairs to complete each level.", cv2.FONT_HERSHEY_SIMPLEX, 3, 2, (255, 255, 255), img, 0, -400)
    centerText("Search the levels to find useful items.", cv2.FONT_HERSHEY_SIMPLEX, 3, 2, (255, 255, 255), img, 0, -300)
    centerText("Avoid enemies during your adventure!", cv2.FONT_HERSHEY_SIMPLEX, 3, 2, (255, 255, 255), img, 0, -200)
    centerText("Use WASD to move.", cv2.FONT_HERSHEY_SIMPLEX, 3, 2, (255, 255, 255), img, 0, 100)
    centerText("Press any key to begin", cv2.FONT_HERSHEY_SIMPLEX, 3, 2, (255, 255, 255), img, 0, 400)
    centerText("Press 'P' to save and 'O' to load.", cv2.FONT_HERSHEY_SIMPLEX, 3, 2, (255, 255, 255), img, 0, 200)
    cv2.imshow("Instructions", img)
    cv2.waitKey(0) # wait for any key to be pressed
    cv2.destroyAllWindows() # destroy window for game to be shown


# game complete screen
def game_complete():
    img = cv2.imread("gameover.png") # background image (black)
    centerText("Game Complete!", cv2.FONT_HERSHEY_SIMPLEX, 5, 2, (255, 255, 255), img, 0, 0) # center text
    centerText("Press Any Key to Close", cv2.FONT_HERSHEY_SIMPLEX, 2, 2, (255, 255, 255), img, 0, 200)
    cv2.imshow("Congrats!", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# game over screen
def show_gameover():
    img = cv2.imread("gameover.png") # background image (black)
    centerText("Game Over!", cv2.FONT_HERSHEY_SIMPLEX, 5, 2, (255, 255, 255), img, 0, 0) # center text
    centerText("Press Any Key to Close", cv2.FONT_HERSHEY_SIMPLEX, 2, 2, (255, 255, 255), img, 0, 200)
    cv2.imshow("Game Over!", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# centering text
def centerText(text, fontFace, fontScale, thickness, color, img, offset_x, offset_y):
    (text_width, text_height), baseline = cv2.getTextSize(text, fontFace, fontScale, thickness) # get width and height of text
    img_height, img_width = img.shape[:2]
    x = (img_width - text_width) // 2           # calculate x and y position
    y = (img_height + text_height) // 2 
    cv2.putText(img, text, (x + offset_x, y + offset_y), fontFace, fontScale, color, thickness) 

# align text - stub
def align(text, fontFace, fontScale, thickness, color, img, side, alignment, offset):
    (text_width, text_height), baseline = cv2.getTextSize(text, fontFace, fontScale, thickness) # get width and height of text
    img_height, img_width = img.shape[:2]
    #cv2.putText(img, text, (x, y), fontFace, fontScale, color, thickness)

# quit screen - stub
def quit_game():
    img = cv2.imread("gameover.png") # background image (black)
    centerText("Quitting Game...", cv2.FONT_HERSHEY_SIMPLEX, 5, 2, (255, 255, 255), img, 0, 0) # center text
    cv2.imshow("Quit Game", img)
    time.sleep(5)
    cv2.destroyAllWindows()