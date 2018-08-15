import curses
from curses import wrapper
from enum import Enum, IntEnum


mainBoard = """xsxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xsxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xaxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xbxxxxxxxx-----xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxsxxxxxxxxx
xxxxxxxxxxxxx*****xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxx***xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxx***xxxxxxxxxxxxxxxxxxxsxxxxxxxxx
xxxxxxxxxxxxxxxxxxx***xxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxmxxxxxxxxxx***xxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxx**xxxxxxx--------xxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxx*xxxxxxxxxxxxxx-xxxxxxxxxxxx
xxxxxxxxxxxxxxxwxxxxxxxxxxxxxbxxxxxxx-xxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-xxxxxxxxxxxx
xxxxxxxxxxxxxxxxxaxxxxxxxxxxxxxxxxxxx-xxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"""

debugStr = ""

class Game:
    def __init__(self):
        self.mode = "play"
        self.hero = Hero()
        self.boards = {}
        self.currBoardId = 0
        self.boardOriginX = 70
        self.boardOriginY = 20

    def initGame(self):
        board = Board()
        self.boards[board.id] = board
        self.hero = Hero()


class Board:
    nextBoardId = 0
    def __init__(self):
        self.id = self.nextBoardId
        self.nextBoardId += 1
        self.grid = []

        board = mainBoard.split("\n")
        for row in board:
            newRow = []
            for cell in row:
                if cell == '-':
                    newRow.append(BoardItem("terrain", "wall"))
                elif cell == '*':
                    newRow.append(BoardItem("terrain", "water"))
                else:
                    newRow.append(BoardItem("terrain", "grass"))
            self.grid.append(newRow)
        
        self.height = len(self.grid)
        self.width = len(self.grid[0])


class BoardItem:
    boardItemNextId = 0
    def __init__(self, mainType, subType):
        self.id = self.boardItemNextId
        self.boardItemNextId += 1
        self.mainType = type
        self.subType = subType

class Hero:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.mods = []
        self.health = 100
        self.inventory = []
        self.equip = {}
    
    def move(self, direction, height, width):
        newX, newY = self.x, self.y
        if direction == MoveDir.UP:
            newY -= 1
        elif direction == MoveDir.DOWN:
            newY += 1
        elif direction == MoveDir.RIGHT:
            newX += 1
        elif direction == MoveDir.LEFT:
            newX -= 1
        
        # Check for bounds
        if newX > 0 and newX < width:
            self.x = newX
        if newY > 0 and newY < height:
            self.y = newY
            


def draw(stdscr, game):
    # What's practical difference between erase and clear?
    # Clears the current screen
    stdscr.erase()

    # Draw board
    board = game.boards[game.currBoardId].grid
    for j, row in enumerate(board):
        for i, cell in enumerate(row):
            x = game.boardOriginX + i
            y = game.boardOriginY + j
            if cell.subType == "water":
                stdscr.addstr(y, x, "*", curses.color_pair(Colors.WATER))
            elif cell.subType == "wall":
                stdscr.addstr(y, x, "-", curses.color_pair(Colors.WALL))
            else:
                stdscr.addstr(y, x, "x", curses.color_pair(Colors.GRASS))

    # Draw hero
    heroX = game.hero.x + game.boardOriginX
    heroY = game.hero.y + game.boardOriginY
    stdscr.addstr(heroY, heroX, "h", curses.color_pair(Colors.HERO))

    # Draw debug panel
    global debugStr
    stdscr.addstr(0, 100, debugStr)

    # Draw 
    stdscr.refresh()

class MoveDir(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

def main(stdscr):
    game = Game()
    game.initGame()

    # Settings for nCurses
    stdscr.nodelay(True)
    curses.curs_set(False)
    initColors()

    while True:
        draw(stdscr, game)
        key = stdscr.getch()
        currBoard = game.boards[game.currBoardId]
        if key == ord("q"):
            break
        elif key == curses.KEY_DOWN:
            game.hero.move(MoveDir.DOWN, currBoard.height, currBoard.width)
        elif key == curses.KEY_UP:
            game.hero.move(MoveDir.UP, currBoard.height, currBoard.width)
        elif key == curses.KEY_RIGHT:
            game.hero.move(MoveDir.RIGHT, currBoard.height, currBoard.width)
        elif key == curses.KEY_LEFT:
            game.hero.move(MoveDir.LEFT, currBoard.height, currBoard.width)
    
class Colors(IntEnum):
    HERO = 1
    TREE = 2
    WATER = 3
    GRASS = 4
    WALL = 5
    WEAPONS = 6

def initColors():
    # pair number, fg, bg
    curses.init_pair(Colors.HERO, 11, 0)
    curses.init_pair(Colors.WATER, 39, 0)
    curses.init_pair(Colors.WALL, 7, 0)
    curses.init_pair(Colors.GRASS, 10, 0)

if __name__ == '__main__':
    # initialize curses
    curses.wrapper(main)

