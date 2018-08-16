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

#################################
# Game
#################################
class Game:
    def __init__(self):
        self.mode = "play"
        self.hero = Hero()
        self.boards = {}
        self.currBoardId = 0
        self.boardOriginX = 70
        self.boardOriginY = 20

    def initGame(self):
        # Initialize all boards.
        # TODO: Probably means this should be done in a for loop?
        board = Board()
        self.boards[board.id] = board
        self.hero = Hero()

#################################
# Board
#################################
class Board:
    nextBoardId = 0
    def __init__(self):
        self.id = self.nextBoardId
        self.nextBoardId += 1
        self.grid = []

        # Eventually when generating terrain, this possibly should just initialize a x by y grid of grass
        board = mainBoard.split("\n")
        for row in board:
            newRow = []
            for cell in row:
                if cell == '-':
                    newRow.append(BoardItem("terrain", "wall"))
                elif cell == '*':
                    newRow.append(BoardItem("terrain", "water"))
                elif cell == "s":
                    newRow.append(BoardItem("item", "sword"))
                elif cell == "a":
                    newRow.append(BoardItem("item", "axe"))
                elif cell == "b":
                    newRow.append(BoardItem("item", "bow"))
                elif cell == "m":
                    newRow.append(BoardItem("item", "mushroom"))
                else:
                    newRow.append(BoardItem("terrain", "grass"))
            self.grid.append(newRow)
        
        self.height = len(self.grid)
        self.width = len(self.grid[0])

        # Generate items?

        # Generate monsters?

        # Generate terrain??


class BoardItem:
    boardItemNextId = 0
    def __init__(self, mainType, subType):
        self.id = self.boardItemNextId
        self.boardItemNextId += 1
        self.mainType = mainType
        self.subType = subType


#################################
# Board
#################################
class Hero:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.mods = []
        self.health = 100
        self.inventory = []
        self.equip = {}
    
    def move(self, board, action):
        height = board.height
        width = board.width

        newX, newY = self.x, self.y
        if action == Actions.UP:
            newY -= 1
        elif action == Actions.DOWN:
            newY += 1
        elif action == Actions.RIGHT:
            newX += 1
        elif action == Actions.LEFT:
            newX -= 1
        
        # Check bounds and if move into next cell?
        if newX >= 0 and newX < width and newY >= 0 and newY < height:
            if not self.isBlocked(board, newX, newY):
                self.x = newX
                self.y = newY

            
    def isBlocked(self, board, newX, newY):
        boardItem = board.grid[newY][newX]
        boardItemType = boardItem.mainType
        boardItemSubType = boardItem.subType

        if boardItemSubType == "grass":
            return False
        if boardItemSubType == "water":
            if "waterwalking" in self.mods:
                return False
        if boardItemType == "terrain" or boardItemType == "monsters":
            return True
        
        # Default to not blocked
        return False

    def pickup(self, board):
        boardItem = board.grid[self.y][self.x]
        # Pick up items
        if boardItem.mainType == "item":
            self.inventory.append(boardItem)
            board.grid[self.y][self.x] = BoardItem("terrain", "grass")



#################################
# Paint
#################################
def draw(stdscr, game):
    # TODO: What's practical difference between erase and clear?
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
            elif cell.subType == "sword":
                stdscr.addstr(y, x, "s", curses.color_pair(Colors.ITEMS))
            elif cell.subType == "axe":
                stdscr.addstr(y, x, "a", curses.color_pair(Colors.ITEMS))
            elif cell.subType == "bow":
                stdscr.addstr(y, x, "b", curses.color_pair(Colors.ITEMS))
            elif cell.subType == "mushroom":
                stdscr.addstr(y, x, "m", curses.color_pair(Colors.ITEMS))
            else:
                stdscr.addstr(y, x, "x", curses.color_pair(Colors.GRASS))

    # Draw hero
    heroX = game.hero.x + game.boardOriginX
    heroY = game.hero.y + game.boardOriginY
    stdscr.addstr(heroY, heroX, "h", curses.color_pair(Colors.HERO))

    # Draw inventory
    stdscr.addstr(0, 0, "Inventory", curses.color_pair(Colors.INVENTORY))
    inventory = game.hero.inventory
    inventoryYIdx = 1
    for item in inventory:
        stdscr.addstr(inventoryYIdx, 0, item.subType, curses.color_pair(Colors.ITEMS))
        inventoryYIdx += 1

    # Draw debug panel
    global debugStr
    stdscr.addstr(0, 100, debugStr)

    # Paint 
    stdscr.refresh()

#################################
# Game Loop
#################################
class Actions(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    

actionMap = {
    curses.KEY_DOWN: Actions.DOWN,
    curses.KEY_UP: Actions.UP,
    curses.KEY_RIGHT: Actions.RIGHT,
    curses.KEY_LEFT: Actions.LEFT,
}

def main(stdscr):
    game = Game()
    game.initGame()
    currBoard = game.boards[game.currBoardId]
    hero = game.hero

    # Settings for nCurses
    curses.curs_set(False)
    initColors()

    while True:
        draw(stdscr, game)
        key = stdscr.getch()
        if key == ord("q"):
            break
        action = actionMap[key]
        hero.move(currBoard, action)
        hero.pickup(currBoard)


#################################
# Helpers
#################################
class Colors(IntEnum):
    HERO = 1
    TREE = 2
    WATER = 3
    GRASS = 4
    WALL = 5
    ITEMS = 6
    INVENTORY = 7

def initColors():
    # pair number, fg, bg
    curses.init_pair(Colors.HERO, 11, 0)
    curses.init_pair(Colors.WATER, 39, 0)
    curses.init_pair(Colors.WALL, 7, 0)
    curses.init_pair(Colors.GRASS, 10, 0)
    curses.init_pair(Colors.ITEMS, 255, 0)
    curses.init_pair(Colors.INVENTORY, 118, 0)


if __name__ == '__main__':
    # initialize curses
    curses.wrapper(main)

