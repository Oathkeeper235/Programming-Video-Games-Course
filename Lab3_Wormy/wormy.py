# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import pygame
import random
import sys
import time

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
BLUE = (137, 207, 240)
DARKBLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0  # syntactic sugar: index of the worm's head

score = 0


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, score

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Wormy')

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()


def runGame():
    # Set a random start point.
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [{'x': startx, 'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}]
    direction = RIGHT

    global score
    start = time.time()

    # Start the apple in a random place.
    apple = getRandomLocation()
    # Start two new flashing objects in random places
    yellowApple = getRandomLocation()
    blueApple = getRandomLocation()
    extraPoints = 0  # new variable for adding extra points to the score

    # Timer for adding the second worm
    second_worm_timer = pygame.time.get_ticks() + 20000  # 20 seconds
    secondWormCoords = []  # Initialize an empty list for the second worm
    secondWormDirection = random.choice([UP, DOWN, LEFT, RIGHT])
    second_worm_change_direction_timer = pygame.time.get_ticks() + 500

    while True:  # main game loop
        current_time = pygame.time.get_ticks()

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

        # check if the worm has hit itself or the edge
        if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or \
                wormCoords[HEAD]['y'] == CELLHEIGHT:
            return  # game over
        for wormBody in wormCoords[1:]:
            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                return  # game over

        # check if worm has eaten an apple
        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            # don't remove worm's tail segment
            apple = getRandomLocation()  # set a new apple somewhere
        else:
            del wormCoords[-1]  # remove worm's tail segment

        # Check if it's time to add the second worm
        if current_time >= second_worm_timer and not secondWormCoords:
            for i in range(5):
                secondWormCoords.append({'x': startx + i, 'y': starty})

        # Move the second worm
        if secondWormCoords:
            moveSecondWorm(secondWormCoords, secondWormDirection, second_worm_change_direction_timer)
            checkCollision(wormCoords, secondWormCoords)

        # Check if worm has eaten one of the two flashing objects
        if wormCoords[HEAD]['x'] == blueApple['x'] and wormCoords[HEAD]['y'] == blueApple['y']:
            blueApple = {'x': -1, 'y': -1}
            extraPoints += 3
        if wormCoords[HEAD]['x'] == yellowApple['x'] and wormCoords[HEAD]['y'] == yellowApple['y']:
            yellowApple = {'x': -1, 'y': -1}
            extraPoints += 3

        # move the worm by adding a segment in the direction it is moving
        if direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        elif direction == RIGHT:
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}

        wormCoords.insert(0, newHead)

        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorm(wormCoords)
        drawWorm(secondWormCoords)  # draw the second worm
        drawApple(apple)
        score = len(wormCoords) - 3 + extraPoints  # New formula for score functionality
        drawScore(score)

        # First flashing object appears for 5 seconds every 5 seconds
        if (time.time() - start) % 10 > 5:
            drawBlueApple(blueApple)

        # Second flashing object appears once for 7 seconds
        if (time.time() - start) < 7:
            drawYellowApple(yellowApple)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


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


def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}


def showGameOverScreen():
    global score

    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)

    # Add score to the game over screen
    scoreFont = pygame.font.Font('freesansbold.ttf', 16)
    scoreSurf = scoreFont.render('Score: ' + str(score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.midtop = (WINDOWWIDTH / 2, 450)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    # Add start and quit buttons to the game over screen
    buttonFont = pygame.font.Font('freesansbold.ttf', 30)
    startSurf = buttonFont.render('Start from the beggining', True, GREEN, DARKGRAY)
    quitSurf = buttonFont.render('Quit', True, GREEN, DARKGRAY)
    startRect = startSurf.get_rect()
    quitRect = quitSurf.get_rect()
    startRect.midtop = (WINDOWWIDTH / 2, 350)
    quitRect.midtop = (WINDOWWIDTH / 2, 400)
    DISPLAYSURF.blit(startSurf, startRect)
    DISPLAYSURF.blit(quitSurf, quitRect)

    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress()  # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get()  # clear event queue
            return
        # Start and quit buttons functionality
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                if startRect.collidepoint(pygame.mouse.get_pos()):
                    return
                if quitRect.collidepoint(pygame.mouse.get_pos()):
                    terminate()


def drawScore(score):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


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


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE):  # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE):  # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


# Add a new function to move the second worm
def moveSecondWorm(wormCoords, direction, change_direction_timer):
    current_time = pygame.time.get_ticks()

    # Check if it's time to change direction
    if current_time >= change_direction_timer:
        direction = random.choice([UP, DOWN, LEFT, RIGHT])

    head = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y']}
    if direction == UP:
        newHead = {'x': head['x'], 'y': head['y'] - 1}
    elif direction == DOWN:
        newHead = {'x': head['x'], 'y': head['y'] + 1}
    elif direction == LEFT:
        newHead = {'x': head['x'] - 1, 'y': head['y']}
    elif direction == RIGHT:
        newHead = {'x': head['x'] + 1, 'y': head['y']}

    wormCoords.insert(0, newHead)
    del wormCoords[-1]


# Add a new function to check collisions between the two worms
def checkCollision(wormCoords, secondWormCoords):
    # Check if the first worm's head collides with the second worm
    if wormCoords[HEAD] in secondWormCoords:
        # Extend the first worm's body
        wormCoords.append({'x': 0, 'y': 0})  # Add a new segment
        # Remove one position from the second worm
        del secondWormCoords[-1]

    # Check if the second worm's head collides with the first worm
    if secondWormCoords[HEAD] in wormCoords:
        # Extend the second worm's body
        secondWormCoords.append({'x': 0, 'y': 0})  # Add a new segment
        # Remove one position from the first worm
        del wormCoords[-1]


def drawYellowApple(coord, flash_count=1):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    flash_duration = 300  # Flash duration in milliseconds
    delay_between_flashes = 300  # Delay between flashes in milliseconds

    start_time = pygame.time.get_ticks()
    flash_state = True
    flash_end_time = start_time + flash_duration

    for _ in range(flash_count):
        current_time = pygame.time.get_ticks()

        if current_time <= flash_end_time:
            pygame.draw.rect(DISPLAYSURF, YELLOW if flash_state else GREEN, pygame.Rect(x, y, CELLSIZE, CELLSIZE))
        else:
            flash_state = not flash_state
            pygame.draw.rect(DISPLAYSURF, YELLOW if flash_state else GREEN, pygame.Rect(x, y, CELLSIZE, CELLSIZE))
            flash_end_time = current_time + delay_between_flashes

        pygame.display.flip()  # Use flip instead of update for better performance
        pygame.event.pump()  # Process events to prevent the window from becoming unresponsive
        FPSCLOCK.tick(FPS)  # Control the frame rate

    # Ensure the final state is drawn after the loop
    pygame.draw.rect(DISPLAYSURF, GREEN, pygame.Rect(x, y, CELLSIZE, CELLSIZE))
    pygame.display.flip()  # Use flip instead of update for better performance


def drawBlueApple(coord, flash_count=1):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    flash_duration = 300  # Flash duration in milliseconds
    delay_between_flashes = 300  # Delay between flashes in milliseconds

    start_time = pygame.time.get_ticks()
    flash_state = True
    flash_end_time = start_time + flash_duration

    for _ in range(flash_count):
        current_time = pygame.time.get_ticks()

        if current_time <= flash_end_time:
            pygame.draw.rect(DISPLAYSURF, DARKBLUE if flash_state else BLUE, pygame.Rect(x, y, CELLSIZE, CELLSIZE))
        else:
            flash_state = not flash_state
            pygame.draw.rect(DISPLAYSURF, DARKBLUE if flash_state else BLUE, pygame.Rect(x, y, CELLSIZE, CELLSIZE))
            flash_end_time = current_time + delay_between_flashes

        pygame.display.flip()  # Use flip instead of update for better performance
        pygame.event.pump()  # Process events to prevent the window from becoming unresponsive
        FPSCLOCK.tick(FPS)  # Control the frame rate

    # Ensure the final state is drawn after the loop
    pygame.draw.rect(DISPLAYSURF, BLUE, pygame.Rect(x, y, CELLSIZE, CELLSIZE))
    pygame.display.flip()  # Use flip instead of update for better performance


if __name__ == '__main__':
    main()
