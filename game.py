import random
import tkinter as tk
from types import SimpleNamespace

from PIL import ImageTk, Image

WIDTH = 800
HEIGHT = 600
w = tk.Tk()
w.geometry(f"{WIDTH}x{HEIGHT}")
canvas = tk.Canvas(w, height=HEIGHT, width=WIDTH)
canvas.place(x=0, y=0, relwidth=1, relheight=1)
# # https://stackoverflow.com/questions/16424091/why-does-tkinter-image-not-show-up-if-created-in-a-function
# photo = ImageTk.PhotoImage(file="doodle.png")
# d = canvas.create_image(400, 400, image=photo)
# photo2 = ImageTk.PhotoImage(file="platform.png")
# p = canvas.create_image(400, 400, image=photo2)
pass

# width and height of each platform and where platforms start
platformWidth = 65
platformHeight = 20
platformStart = HEIGHT - 50

# player physics
GRAVITY = 0.33
DRAG = 0.3
BOUNCE_VELOCITY = -12.5

# minimum and maximum vertical space between each platform
minPlatformSpace = 15
maxPlatformSpace = 20

# information about each platform. the first platform starts in the
# bottom middle of the screen
platforms = [SimpleNamespace(
    x=WIDTH / 2 - platformWidth / 2,
    y=platformStart
)]

#  fill the initial screen with platforms
y = platformStart
while y > 0:
    # the next platform can be placed above the previous one with a space
    # somewhere between the min and max space
    y -= platformHeight + random.uniform(minPlatformSpace, maxPlatformSpace)
    # a platform can be placed anywhere 25px from the left edge of the canvas
    # and 25px from the right edge of the canvas (taking into account platform
    # width).
    # however the first few platforms cannot be placed in the center so
    # that the player will bounce up and down without going up the screen
    # until they are ready to move
    x = None
    while True:
        x = random.uniform(25, WIDTH - 25 - platformWidth)
        if not (y > HEIGHT / 2 and WIDTH / 2 - platformWidth * 1.5 < x < WIDTH / 2 + platformWidth / 2):
            break

    platforms.append(SimpleNamespace(x=x, y=y))

# the doodle jumper
DOODLE = SimpleNamespace(
    width=40,
    height=60,
    x=WIDTH / 2 - 20,
    y=platformStart - 60,
    # velocity
    dx=0,
    dy=0
)
# 
# keep track of player direction and actions
playerDir = 0
keydown = False
prevDoodleY = DOODLE.y


# game loop
def loop():
    global minPlatformSpace, maxPlatformSpace, playerDir, platforms, prevDoodleY
    canvas.after(17, loop) #17 is 1000//60

    canvas.delete("all")

    # apply GRAVITY to doodle
    DOODLE.dy += GRAVITY
    #
    #     if doodle reaches the middle of the screen, move the platforms down
    #     instead of doodle up to make it look like doodle is going up
    if DOODLE.y < HEIGHT / 2 and DOODLE.dy < 0:
        for platform in platforms:
            platform.y += -DOODLE.dy
        #
        #       add more platforms to the top of the screen as doodle moves up
        while platforms[len(platforms) - 1].y > 0:
            platforms.append(SimpleNamespace(
                x=random.uniform(25, WIDTH - 25 - platformWidth),
                y=platforms[len(platforms) - 1].y - (platformHeight + random.uniform(minPlatformSpace, maxPlatformSpace))
            ))
        #
        #         add a bit to the min/max platform space as the player goes up
            minPlatformSpace += 0.5
            maxPlatformSpace += 0.5
            #
            #         cap max space
            maxPlatformSpace = min(maxPlatformSpace, HEIGHT / 2)
    else:
        DOODLE.y += DOODLE.dy

    #     only apply DRAG to horizontal movement if key is not pressed
    if not keydown:
        if playerDir < 0:
            DOODLE.dx += DRAG
            #
            #         // don't let dx go above 0
            if DOODLE.dx > 0:
                DOODLE.dx = 0
                playerDir = 0
        #
        elif playerDir > 0:
            DOODLE.dx -= DRAG
            #
            if DOODLE.dx < 0:
                DOODLE.dx = 0
                playerDir = 0

    DOODLE.x += DOODLE.dx
    #
    #   make doodle wrap the screen
    if DOODLE.x + DOODLE.width < 0:
        DOODLE.x = WIDTH
    elif DOODLE.x > WIDTH:
        DOODLE.x = -DOODLE.width

    #     draw platforms
    for platform in platforms:
        canvas.create_rectangle(platform.x, platform.y,
                                platform.x+platformWidth, platform.y+platformHeight,fill="green")

    for platform in platforms:
        #     make doodle jump if it collides with a platform from above
        if (
                # doodle is falling
                DOODLE.dy > 0 and
                # doodle was previous above the platform
                prevDoodleY + DOODLE.height <= platform.y and
                # doodle collides with platform
                # (Axis Aligned Bounding Box [AABB] collision check)
                DOODLE.x < platform.x + platformWidth and
                DOODLE.x + DOODLE.width > platform.x and
                DOODLE.y < platform.y + platformHeight and
                DOODLE.y + DOODLE.height > platform.y
        ):
            # reset doodle position so it's on top of the platform
            DOODLE.y = platform.y - DOODLE.height
            DOODLE.dy = BOUNCE_VELOCITY

    # draw doodle
    canvas.create_rectangle(DOODLE.x, DOODLE.y,
                            DOODLE.x+DOODLE.width, DOODLE.y+DOODLE.height,fill="yellow")

    prevDoodleY = DOODLE.y
    #    remove any platforms that have gone offscreen
    platforms = [platform for platform in platforms if platform.y < HEIGHT]


def handle_key_press(e):
    global keydown,playerDir
    if e.keysym == "Right":
        keydown = True
        playerDir = -1
        DOODLE.dx = 3
    elif e.keysym == "Left":
        keydown = True
        playerDir = 1
        DOODLE.dx = -3


def handle_key_release(e):
    global keydown
    keydown = False


# Tkinter reacts to holding key as key repeating same with canvas
# https://stackoverflow.com/questions/27215326/tkinter-keypress-keyrelease-events
# so use canvas' But that's not a problem here

w.bind("<KeyPress>", handle_key_press)
w.bind("<KeyRelease>", handle_key_release)

canvas.after(17,loop) #17 is 1000//60

w.mainloop()
