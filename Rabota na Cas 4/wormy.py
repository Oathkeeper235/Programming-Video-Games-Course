# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys
from pygame.locals import *

FPS = 15
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 155, 0)
DARKGRAY = (40, 40, 40)
YELLOW = (255, 255, 0)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0  # syntactic sugar: index of the worm's head
score = 0

YELLOW_APPLE = {'x': -1, 'y': -1, 'timeout': 0, 'active': False}
YELLOW_APPLE_TIMEOUT = 8000  # Time in milliseconds for yellow apple to appear

SPEED_BOOST = {'x': -1, 'y': -1, 'timeout': 0, 'active': False}
SPEED_BOOST_TIMEOUT = 5000  # Time in milliseconds for the speed boost to last
NORMAL_SPEED = 15  # Normal speed of the game
BOOSTED_SPEED = 25  # Speed during the boost


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Wormy')

    showStartScreen()
    while True:
        runGame(score)
        showGameOverScreen()


def runGame(score):
    # Set a random start point.
    global YELLOW_APPLE
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [{'x': startx, 'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}]
    direction = RIGHT

    # Start the apple in a random place.
    apple = getRandomLocation()

    speed_boost_active = False  # Track if the speed boost is currently active
    current_speed = NORMAL_SPEED  # Initialize the speed

    while True:  # main game loop
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()

        # check if the worms has hit a wall
        """
        if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or \
                wormCoords[HEAD]['y'] == CELLHEIGHT:
            return  # game over
        """
        # check if the worm has hit itself
        for wormBody in wormCoords[1:]:
            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                return  # game over

        # check if worm has eaten a yellow apple
        if wormCoords[HEAD]['x'] == YELLOW_APPLE['x'] and wormCoords[HEAD]['y'] == YELLOW_APPLE['y']:
            YELLOW_APPLE['active'] = False  # deactivate the yellow apple
            del wormCoords[-1]  # remove worm's tail segment

        # check if worm has eaten a red apple
        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            # don't remove worm's tail segment
            apple = getRandomLocation()  # set a new apple somewhere
            score += 1
        else:
            del wormCoords[-1]  # remove worm's tail segment

        # check if worm has eaten a speed boost
        if wormCoords[HEAD]['x'] == SPEED_BOOST['x'] and wormCoords[HEAD]['y'] == SPEED_BOOST['y']:
            SPEED_BOOST['active'] = False  # deactivate the speed boost
            speed_boost_active = True  # activate the speed boost
            SPEED_BOOST['timeout'] = pygame.time.get_ticks() + SPEED_BOOST_TIMEOUT
            current_speed = BOOSTED_SPEED  # set the speed to boosted

        # check if the speed boost has expired
        if speed_boost_active and pygame.time.get_ticks() > SPEED_BOOST['timeout']:
            speed_boost_active = False
            current_speed = NORMAL_SPEED  # reset the speed to normal

        # Generate a new speed boost if it's not active
        if not SPEED_BOOST['active']:
            SPEED_BOOST['x'] = getRandomLocation(exclude=wormCoords + [apple, YELLOW_APPLE, SPEED_BOOST])['x']
            SPEED_BOOST['y'] = getRandomLocation(exclude=wormCoords + [apple, YELLOW_APPLE, SPEED_BOOST])['y']
            SPEED_BOOST['active'] = True

        # move the worm by adding a segment in the direction it is moving
        if direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        elif direction == RIGHT:
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}

        # Handle screen wrapping for the worm's head
        if newHead['x'] < 0:
            newHead['x'] = CELLWIDTH - 1
        elif newHead['x'] >= CELLWIDTH:
            newHead['x'] = 0

        if newHead['y'] < 0:
            newHead['y'] = CELLHEIGHT - 1
        elif newHead['y'] >= CELLHEIGHT:
            newHead['y'] = 0

        wormCoords.insert(0, newHead)

        # Generate a new yellow apple if it's not active
        if not YELLOW_APPLE['active']:
            YELLOW_APPLE = {'x': -1, 'y': -1, 'timeout': pygame.time.get_ticks() + YELLOW_APPLE_TIMEOUT, 'active': True}
            YELLOW_APPLE['x'] = getRandomLocation(exclude=wormCoords + [apple, YELLOW_APPLE])['x']
            YELLOW_APPLE['y'] = getRandomLocation(exclude=wormCoords + [apple, YELLOW_APPLE])['y']

        # Check if the yellow apple has expired
        if pygame.time.get_ticks() > YELLOW_APPLE['timeout']:
            YELLOW_APPLE['active'] = False

        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorm(wormCoords)
        drawApple(apple)
        drawYellowApple(YELLOW_APPLE)
        drawScore(score, speed_boost_active)
        drawSpeedBoost(SPEED_BOOST)
        pygame.display.update()
        FPSCLOCK.tick(current_speed)


def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('Wormy!', True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get()  # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3  # rotate by 3 degrees each frame
        degrees2 += 7  # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()


# def getRandomLocation():
#     return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}

# avoid placing apples on the worm
def getRandomLocation(exclude=[]):
    location = {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}
    while location in exclude:
        location = {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}
    return location


def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    YELLOW_APPLE['active'] = False  # reset the yellow apple

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress()  # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get()  # clear event queue
            return


def drawScore(score, speed_boost_active):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    if speed_boost_active:
        boostSurf = BASICFONT.render('Speed Boost!', True, (0, 255, 255))
        boostRect = boostSurf.get_rect()
        boostRect.topleft = (WINDOWWIDTH - 120, 40)
        DISPLAYSURF.blit(boostSurf, boostRect)


def drawWorm(wormCoords):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)


def drawYellowApple(coord):
    if coord['active']:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        yellowAppleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, YELLOW, yellowAppleRect)


def drawSpeedBoost(coord):
    if coord['active']:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        speedBoostRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, (0, 255, 255), speedBoostRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE):  # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE):  # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()
