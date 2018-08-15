import curses
from curses import wrapper


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
        self.boards = {}
        self.hero = Hero()
        self.mode = "play"
        self.currBoardId = 0
        self.boardOriginX = 70
        self.boardOriginY = 20

    def initGame(self):
        board = Board()
        self.boards[board.id] = board


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
                stdscr.addch(y, x, "*")
            elif cell.subType == "wall":
                stdscr.addch(y, x, "-")
            else:
                stdscr.addch(y, x, "x")


    # Draw debug panel
    global debugStr
    stdscr.addstr(0, 100, debugStr)

    # Draw 
    stdscr.refresh()


def main(stdscr):
    game = Game()
    game.initGame()

    # Settings for nCurses
    stdscr.nodelay(True)
    curses.curs_set(False)

    while True:
        draw(stdscr, game)
        key = stdscr.getch()
        if key == ord("q"):
            break
    

if __name__ == '__main__':
    # initialize curses
    curses.wrapper(main)

