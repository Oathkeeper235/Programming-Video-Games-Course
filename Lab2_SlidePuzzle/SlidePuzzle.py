# Slide Puzzle
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import pygame, sys, random
from pygame.locals import *

# Create the constants (go ahead and experiment with different values)

# BOARDWIDTH = 4  # number of columns in the board
# BOARDHEIGHT = 4  # number of rows in the board
# Za brojot na polinja vo redicite i kolonite da e razlicen tablata ke ja napravime 8x6 kako vo primerot.
BOARDWIDTH = 8  # Brojot na redici sega ke bide 8
BOARDHEIGHT = 6  # Brojot na koloni sega ke bide 6

TILESIZE = 80

# WINDOWWIDTH = 640
# WINDOWHEIGHT = 480
# Za novata tabla koja ima 8 redici i 6 koloni da e pregledna mora da gi zgolemime shirinata i visinata na prozorecot.
WINDOWWIDTH = 840  # Novata shirina na prozorecot e 840.
WINDOWHEIGHT = 700  # Novata visina na prozorecot e 700.
FPS = 30
BLANK = None

#                 R    G    B
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BRIGHTBLUE = (0, 50, 255)
DARKTURQUOISE = (3, 54, 73)
GREEN = (0, 204, 0)

BGCOLOR = DARKTURQUOISE
TILECOLOR = GREEN
TEXTCOLOR = WHITE
BORDERCOLOR = BRIGHTBLUE
BASICFONTSIZE = 20

BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE

XMARGIN = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) / 2)
YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 2)

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HELP_TEXT = "Click a tile or press an arrow key to move it.\n" \
            "Your goal is to solve the puzzle by arranging the tiles\n" \
            "in ascending order, with the blank space in the bottom-right.\n" \
            "Tiles can only move to adjacent empty spaces."

# Dodadeni se promenlivi za blankxpos i blankypos poradi tretoto baranje
blankxpos = BOARDWIDTH - 1  # Inicijalna pozicija na praznoto pole
blankypos = BOARDHEIGHT - 1


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, RESET_SURF, RESET_RECT, NEW_SURF, NEW_RECT, SOLVE_SURF, SOLVE_RECT, HELP_SURF, HELP_RECT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Slide Puzzle')
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

    # Store the option buttons and their rectangles in OPTIONS.
    RESET_SURF, RESET_RECT = makeText('Reset', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 90)
    NEW_SURF, NEW_RECT = makeText('New Game', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 60)
    SOLVE_SURF, SOLVE_RECT = makeText('Solve', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 30)

    # Create the "Help" button and its rectangle.
    HELP_SURF, HELP_RECT = makeText('Help', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 120)

    mainBoard, solutionSeq = generateNewPuzzle(80)
    SOLVEDBOARD = getStartingBoard()  # a solved board is the same as the board in a start state.
    allMoves = []  # list of moves made from the solved configuration

    while True:  # main game loop
        slideTo = None  # the direction, if any, a tile should slide
        msg = 'Click tile or press arrow keys to slide.'  # contains the message to show in the upper left corner.
        if mainBoard == SOLVEDBOARD:
            msg = 'Solved!'

        drawBoard(mainBoard, msg)

        checkForQuit()
        for event in pygame.event.get():  # event handling loop
            if event.type == MOUSEBUTTONUP:
                spotx, spoty = getSpotClicked(mainBoard, event.pos[0], event.pos[1])

                if (spotx, spoty) == (None, None):
                    # check if the user clicked on an option button
                    if RESET_RECT.collidepoint(event.pos):
                        resetAnimation(mainBoard, allMoves)  # clicked on Reset button
                        allMoves = []
                    elif NEW_RECT.collidepoint(event.pos):
                        mainBoard, solutionSeq = generateNewPuzzle(80)  # clicked on New Game button
                        allMoves = []
                    elif SOLVE_RECT.collidepoint(event.pos):
                        resetAnimation(mainBoard, solutionSeq + allMoves)  # clicked on Solve button
                        allMoves = []
                    elif HELP_RECT.collidepoint(event.pos):
                        # Display the help message and highlight adjacent fields.
                        displayHelpMessage(mainBoard)
                else:
                    # check if the clicked tile was next to the blank spot

                    blankx, blanky = getBlankPosition(mainBoard)
                    if spotx == blankx + 1 and spoty == blanky:
                        slideTo = LEFT
                    elif spotx == blankx - 1 and spoty == blanky:
                        slideTo = RIGHT
                    elif spotx == blankx and spoty == blanky + 1:
                        slideTo = UP
                    elif spotx == blankx and spoty == blanky - 1:
                        slideTo = DOWN

            elif event.type == KEYUP:
                # check if the user pressed a key to slide a tile
                if event.key in (K_LEFT, K_a) and isValidMove(mainBoard, LEFT):
                    slideTo = LEFT
                elif event.key in (K_RIGHT, K_d) and isValidMove(mainBoard, RIGHT):
                    slideTo = RIGHT
                elif event.key in (K_UP, K_w) and isValidMove(mainBoard, UP):
                    slideTo = UP
                elif event.key in (K_DOWN, K_s) and isValidMove(mainBoard, DOWN):
                    slideTo = DOWN

        if slideTo:
            slideAnimation(mainBoard, slideTo, 'Click tile or press arrow keys to slide.', 8)  # show slide on screen
            makeMove(mainBoard, slideTo)
            allMoves.append(slideTo)  # record the slide
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


def checkForQuit():
    for event in pygame.event.get(QUIT):  # get all the QUIT events
        terminate()  # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP):  # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate()  # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event)  # put the other KEYUP event objects back


def getStartingBoard():
    # Return a board data structure with tiles in the solved state.
    # For example, if BOARDWIDTH and BOARDHEIGHT are both 3, this function
    # returns [[1, 4, 7], [2, 5, 8], [3, 6, BLANK]]
    counter = 1
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(counter)
            counter += BOARDWIDTH
        board.append(column)
        counter -= BOARDWIDTH * (BOARDHEIGHT - 1) + BOARDWIDTH - 1

    board[BOARDWIDTH - 1][BOARDHEIGHT - 1] = BLANK
    return board


def getBlankPosition(board):
    # Return the x and y of board coordinates of the blank space.
    # Funkcijata gi vrakja promenlivite koi se cuvaat
    return (blankxpos, blankypos)


# Napraveni se promeni vo funkcijata za da se iskoristat globalnite promenlivi.
def makeMove(board, move):
    global blankxpos, blankypos
    # This function does not check if the move is valid.

    # Soodvetno vo site sluchai se azhuriraat koordinatite na praznoto pole.
    if move == UP:
        board[blankxpos][blankypos], board[blankxpos][blankypos + 1] = (
            board[blankxpos][blankypos + 1], board[blankxpos][blankypos],
        )
        blankypos += 1
    elif move == DOWN:
        board[blankxpos][blankypos], board[blankxpos][blankypos - 1] = (
            board[blankxpos][blankypos - 1], board[blankxpos][blankypos],
        )
        blankypos -= 1
    elif move == LEFT:
        board[blankxpos][blankypos], board[blankxpos + 1][blankypos] = (
            board[blankxpos + 1][blankypos], board[blankxpos][blankypos],
        )
        blankxpos += 1
    elif move == RIGHT:
        board[blankxpos][blankypos], board[blankxpos - 1][blankypos] = (
            board[blankxpos - 1][blankypos], board[blankxpos][blankypos],
        )
        blankxpos -= 1


def isValidMove(board, move):
    blankx, blanky = getBlankPosition(board)
    return (move == UP and blanky != len(board[0]) - 1) or \
        (move == DOWN and blanky != 0) or \
        (move == LEFT and blankx != len(board) - 1) or \
        (move == RIGHT and blankx != 0)


def getRandomMove(board, lastMove=None):
    # start with a full list of all four moves
    validMoves = [UP, DOWN, LEFT, RIGHT]

    # remove moves from the list as they are disqualified
    if lastMove == UP or not isValidMove(board, DOWN):
        validMoves.remove(DOWN)
    if lastMove == DOWN or not isValidMove(board, UP):
        validMoves.remove(UP)
    if lastMove == LEFT or not isValidMove(board, RIGHT):
        validMoves.remove(RIGHT)
    if lastMove == RIGHT or not isValidMove(board, LEFT):
        validMoves.remove(LEFT)

    # return a random move from the list of remaining moves
    return random.choice(validMoves)


def getLeftTopOfTile(tileX, tileY):
    left = XMARGIN + (tileX * TILESIZE) + (tileX - 1)
    top = YMARGIN + (tileY * TILESIZE) + (tileY - 1)
    return (left, top)


def getSpotClicked(board, x, y):
    # from the x & y pixel coordinates, get the x & y board coordinates
    for tileX in range(len(board)):
        for tileY in range(len(board[0])):
            left, top = getLeftTopOfTile(tileX, tileY)
            tileRect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if tileRect.collidepoint(x, y):
                return (tileX, tileY)
    return (None, None)


def drawTile(tilex, tiley, number, adjx=0, adjy=0):
    # draw a tile at board coordinates tilex and tiley, optionally a few
    # pixels over (determined by adjx and adjy)
    left, top = getLeftTopOfTile(tilex, tiley)
    pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left + adjx, top + adjy, TILESIZE, TILESIZE))
    textSurf = BASICFONT.render(str(number), True, TEXTCOLOR)
    textRect = textSurf.get_rect()
    textRect.center = left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy
    DISPLAYSURF.blit(textSurf, textRect)


def makeText(text, color, bgcolor, top, left):
    # create the Surface and Rect objects for some text.
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)


def drawBoard(board, message):
    DISPLAYSURF.fill(BGCOLOR)
    if message:
        textSurf, textRect = makeText(message, MESSAGECOLOR, BGCOLOR, 5, 5)
        DISPLAYSURF.blit(textSurf, textRect)

    for tilex in range(len(board)):
        for tiley in range(len(board[0])):
            if board[tilex][tiley]:
                drawTile(tilex, tiley, board[tilex][tiley])

    left, top = getLeftTopOfTile(0, 0)
    width = BOARDWIDTH * TILESIZE
    height = BOARDHEIGHT * TILESIZE
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)

    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
    DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)
    DISPLAYSURF.blit(HELP_SURF, HELP_RECT)  # Za renderiranje na HELP kopceto.

    pygame.display.update()


def slideAnimation(board, direction, message, animationSpeed):
    # Note: This function does not check if the move is valid.

    blankx, blanky = getBlankPosition(board)
    if direction == UP:
        movex = blankx
        movey = blanky + 1
    elif direction == DOWN:
        movex = blankx
        movey = blanky - 1
    elif direction == LEFT:
        movex = blankx + 1
        movey = blanky
    elif direction == RIGHT:
        movex = blankx - 1
        movey = blanky

    # prepare the base surface
    drawBoard(board, message)
    baseSurf = DISPLAYSURF.copy()
    # draw a blank space over the moving tile on the baseSurf Surface.
    moveLeft, moveTop = getLeftTopOfTile(movex, movey)
    pygame.draw.rect(baseSurf, BGCOLOR, (moveLeft, moveTop, TILESIZE, TILESIZE))

    for i in range(0, TILESIZE, animationSpeed):
        # animate the tile sliding over
        checkForQuit()
        DISPLAYSURF.blit(baseSurf, (0, 0))
        if direction == UP:
            drawTile(movex, movey, board[movex][movey], 0, -i)
        if direction == DOWN:
            drawTile(movex, movey, board[movex][movey], 0, i)
        if direction == LEFT:
            drawTile(movex, movey, board[movex][movey], -i, 0)
        if direction == RIGHT:
            drawTile(movex, movey, board[movex][movey], i, 0)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generateNewPuzzle(numSlides):
    # From a starting configuration, make numSlides number of moves (and
    # animate these moves).
    sequence = []
    board = getStartingBoard()
    drawBoard(board, '')
    pygame.display.update()
    pygame.time.wait(500)  # pause 500 milliseconds for effect
    lastMove = None
    for i in range(numSlides):
        move = getRandomMove(board, lastMove)
        slideAnimation(board, move, 'Generating new puzzle...', animationSpeed=int(TILESIZE / 3))
        makeMove(board, move)
        sequence.append(move)
        lastMove = move
    return (board, sequence)


def resetAnimation(board, allMoves):
    # make all of the moves in allMoves in reverse.
    revAllMoves = allMoves[:]  # gets a copy of the list
    revAllMoves.reverse()

    for move in revAllMoves:
        if move == UP:
            oppositeMove = DOWN
        elif move == DOWN:
            oppositeMove = UP
        elif move == RIGHT:
            oppositeMove = LEFT
        elif move == LEFT:
            oppositeMove = RIGHT
        slideAnimation(board, oppositeMove, '', animationSpeed=int(TILESIZE / 2))
        makeMove(board, oppositeMove)


def displayHelpMessage(mainBoard):
    help_lines = HELP_TEXT.split('\n')

    # Presmetaj ja vkupnata visina potrebna za site linii.
    total_height = (len(help_lines)) * BASICFONTSIZE

    drawBoard(mainBoard, "")  # Prikazhi prazna tabla.

    # Oboi gi site polinja sosedni na praznoto vo crvena boja.
    blankx, blanky = getBlankPosition(mainBoard)
    adjacentTiles = [(blankx + 1, blanky), (blankx - 1, blanky), (blankx, blanky + 1), (blankx, blanky - 1)]
    for tilex, tiley in adjacentTiles:
        if 0 <= tilex < BOARDWIDTH and 0 <= tiley < BOARDHEIGHT:
            left, top = getLeftTopOfTile(tilex, tiley)
            pygame.draw.rect(DISPLAYSURF, (255, 0, 0), (left, top, TILESIZE, TILESIZE), 3)

    # Prikazhi go "BACK" kopceto za vrakjanje nazad.
    BACK_SURF, BACK_RECT = makeText('Back', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 90)
    DISPLAYSURF.blit(BACK_SURF, BACK_RECT)

    # Prikazhi ja porakata so mozhna nasoka za pridvizuvanje vo sledniot cekor.
    best_move = getRandomMove(mainBoard)
    if best_move is not None:
        hint_text = f"Hint: You can move {best_move.capitalize()} for the next step."
        textSurf = BASICFONT.render(hint_text, True, TEXTCOLOR, BGCOLOR)
        textRect = textSurf.get_rect()
        textRect.topleft = (5, total_height)  # Prilagodi go top koordinatot.
        DISPLAYSURF.blit(textSurf, textRect)

    # Prikazhi go help tekstot.
    for i, line in enumerate(help_lines):
        textSurf = BASICFONT.render(line, True, TEXTCOLOR, BGCOLOR)
        textRect = textSurf.get_rect()
        textRect.topleft = (5, i * BASICFONTSIZE)
        DISPLAYSURF.blit(textSurf, textRect)

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                if BACK_RECT.collidepoint(event.pos):
                    return  # Vrati se nazad vo igrata :)


if __name__ == '__main__':
    main()
