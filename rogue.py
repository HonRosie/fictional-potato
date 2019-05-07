import copy
import curses
import random
import time
from terrain import terrainDict
from gameInfo import levelInfo, randomLevelItems, requiredLevelItems
from curses import wrapper
from enum import Enum, IntEnum
from generateRooms import generateRooms
from boardCell import Type, BACKGROUND, WATER, WALL, GRASS, DOORUNLOCKED


debugStr = ""

#################################
# Game
#################################
class Modes(Enum):
    PLAY = 1
    INVENTORY = 2
    COOK = 3


class Game:
    def __init__(self, stdscr, seed):
        global debugStr
        # Game states
        self.mode = Modes.PLAY
        self.isGameOver = False
        # board
        self.boardOriginX = None
        self.boardOriginY = None
        self.boards = {}
        board = Board(stdscr, seed)
        self.currBoardId = board.id
        self.boards[board.id] = board

        # Hero
        self.hero = Hero(board)

        # Misc
        self.messages = []


    def changeGameMode(self, action, newHero):
        global debugStr
        if self.mode == Modes.PLAY:
            if action == Actions.INVENTORY:
                newHero.selectedItemIdx = 0
                self.mode = Modes.INVENTORY
            return

        elif self.mode == Modes.INVENTORY:
            if action == Actions.INVENTORY:
                newHero.selectedItemIdx = 0
                self.mode = Modes.PLAY
            return

gameItems = {
    BACKGROUND: {"type": Type.TERRAIN},
    GRASS: {"type": Type.TERRAIN},
    WALL: {"type": Type.TERRAIN},
    WATER: {"type": Type.TERRAIN},
    DOORUNLOCKED: {"type": Type.TERRAIN},
}

#################################
# Board/Items
#################################
class Board:
    nextBoardId = 0
    nextItemId = 5
    def __init__(self, stdscr, seed):
        global debugStr
        self.id = Board.nextBoardId
        Board.nextBoardId += 1
        grid, roomList = generateRooms(stdscr, seed)
        self.grid = grid
        self.height = len(self.grid)
        self.width = len(self.grid[0])
        self.generateWeapons(roomList, seed)

    def generateWeapons(self, roomList, seed):
        global debugStr
        random.seed(seed)
        ######### temp solution #########
        # pick random location 
        axe = {"itemId": Board.nextItemId, "type": Type.WEAPON, "subtype": "axe", "name": "Axe"}
        gameItems[axe["itemId"]] = axe
        Board.nextItemId += 1
        sword = {"itemId": Board.nextItemId, "type": Type.WEAPON, "subtype": "sword", "name": "Sword"}
        gameItems[sword["itemId"]] = sword
        Board.nextItemId += 1
        bow = {"itemId": Board.nextItemId, "type": Type.WEAPON, "subtype": "bow", "name": "Bow"}
        gameItems[bow["itemId"]] = bow
        Board.nextItemId += 1
        randomRooms = random.sample(roomList, 2)
        for room in randomRooms:
            x, y = self.getRandomValidPosInRoom(room, seed)
            self.grid[y][x] = sword["itemId"]
            debugStr += str(x) + "," + str(y) + " | "
        randomRooms = random.sample(roomList, 2)
        for room in randomRooms:
            x, y = self.getRandomValidPosInRoom(room, seed)
            self.grid[y][x] = bow["itemId"]
            debugStr += str(x) + "," + str(y) + " | "
        randomRooms = random.sample(roomList, 1)
        for room in randomRooms:
            x, y = self.getRandomValidPosInRoom(room, seed)
            self.grid[y][x] = axe["itemId"]
            debugStr += str(x) + "," + str(y) + " | "
    

    def getRandomValidPosInRoom(self, room, seed):
        global debugStr
        random.seed(seed)
        while True:
            x = random.randint(room.left, room.right)
            y = random.randint(room.top, room.bottom)
            if self.grid[y][x] == GRASS:
                # debugStr += str(self.id) + ":" + str(x) + "," + str(y) + " | "
                return x, y


#################################
# Hero
#################################
class Hero:
    def __init__(self, board):
        # TODO Hero can spawn outside a room this way
        self.x = int(board.width/2)
        self.y = int(board.height/2)
        self.mods = set()
        self.health = 100
        self.inventory = {} # map[itemId]count
        self.orderedInventory = [] # [itemId]
        self.selectedItemIdx = 0

    #################################
    # Hero movement
    #################################
    def computeNewPos(self, board, action, ignoreObstacles):
        global debugStr
        newX, newY = self.x, self.y
        if action == Actions.UP:
            newY -= 1
        elif action == Actions.DOWN:
            newY += 1
        elif action == Actions.RIGHT:
            newX += 1
        elif action == Actions.LEFT:
            newX -= 1

        # Check bounds and if should return new or old position
        if newX >= 0 and newX < board.width and newY >= 0 and newY < board.height:
            if ignoreObstacles or not self.isBlocked(board, newX, newY):
                return newX, newY
        return self.x, self.y

    def move(self, game, action, newHero):
        global debugStr
        board = game.boards[game.currBoardId]
        newX, newY = self.computeNewPos(board, action, False)
        newHero.x = newX
        newHero.y = newY

    def isBlocked(self, board, newX, newY):
        global debugStr
        cell = board.grid[newY][newX]
        cellType = gameItems[cell]["type"]

        if cell == GRASS:
            return False
        if cell == DOORUNLOCKED:
            return False
        if cell == WATER:
            if "waterwalking" in self.mods:
                return False
        if cellType == Type.TERRAIN:
            return True
        
        # Default to not blocked
        return False

    #################################
    # Pickup item
    #################################
    def pickup(self, board, action, newHero):
        global debugStr
        newX, newY = self.computeNewPos(board, action, False)
        # Check if there's an item at hero's x,y coordinates    
        itemId = board.grid[newY][newX]
        itemType = gameItems[itemId]["type"]

        # Add item to inventory and orderedInventory
        if itemType == Type.WEAPON:
            newHero.addToInventory(itemId)
            board.grid[newY][newX] = GRASS
            debugStr += str(newHero.orderedInventory) + " | "


    #################################
    # Inventory/Equipment management
    #################################
    def moveSelection(self, items, action, newHero):
        global debugStr
        numItems = len(items.keys())
        # Move selection down/up
        if action == Actions.DOWN:
            if self.selectedItemIdx < numItems-1:
                newHero.selectedItemIdx += 1
        if action == Actions.UP:
            if self.selectedItemIdx > 0:
                newHero.selectedItemIdx -= 1
        # debugStr += str(newHero.selectedItemIdx) + " | "

    def addToInventory(self, itemId):
        if itemId in self.inventory:
            self.inventory[itemId] += 1
        else:
            self.inventory[itemId] = 1
            self.orderedInventory.append(itemId)
            self.orderedInventory.sort(key=lambda itemId: gameItems[itemId]["name"])

    def removeFromInventory(self, itemId):
        self.inventory[itemId] -= 1
        if self.inventory[itemId] == 0:
            del self.inventory[itemId]
            self.orderedInventory.remove(itemId)


#################################
# Paint
#################################
def resize(stdscr, game):
    global debugStr
    maxY, maxX = stdscr.getmaxyx()
    curses.resizeterm(maxY, maxX)

    middleY = maxY/2
    game.boardOriginY = int(middleY - game.boards[game.currBoardId].height/2)
    middleX = maxX/2
    game.boardOriginX = int(middleX - game.boards[game.currBoardId].width/2)

    return maxY, maxX

# Draws a bunch of items in a list(non-Pythonic) format
def drawInventory(stdscr, game, items, title, posX, posY, displaySelector):
    global debugStr
    # Draw title
    stdscr.addstr(posY, posX, title, curses.color_pair(Colors.INVENTORY))
    posY += 1

    # items -> [itemIds]
    itemColor = curses.color_pair(Colors.ITEMS)
    for idx, itemId in enumerate(items):
        name = gameItems[itemId]["name"]
        # append quantity
        numItems = game.hero.inventory[itemId]
        if numItems > 1:
            numString = " (" + str(numItems) + ")"
            name += numString
        # append selection asterik
        if idx == game.hero.selectedItemIdx and displaySelector:
            name += " * "
        stdscr.addstr(posY, posX, name, itemColor)
        posY += 1


def drawBoard(stdscr, game, boardX, boardY):
    board = game.boards[game.currBoardId].grid
    for j, row in enumerate(board):
        for i, cell in enumerate(row):
            cellType = gameItems[cell]["type"]
            x = boardX + i
            y = boardY + j
            if cell == BACKGROUND:
                stdscr.addstr(y, x, "", curses.color_pair(Colors.WATER))
            elif cell == DOORUNLOCKED:
                stdscr.addstr(y, x, "+", curses.color_pair(Colors.WATER))
            elif cell == WALL:
                stdscr.addstr(y, x, "#", curses.color_pair(Colors.WALL))
            elif cell == WATER:
                stdscr.addstr(y, x, "~", curses.color_pair(Colors.WATER))
            elif cellType == Type.WEAPON:
                stdscr.addstr(y, x, "&", curses.color_pair(Colors.HERO))
            else:
                stdscr.addstr(y, x, ".", curses.color_pair(Colors.GRASS))

def drawHero(stdscr, game, heroX, heroY):
    stdscr.addstr(heroY, heroX, "h", curses.color_pair(Colors.HERO))


def drawPlayMode(stdscr, game, maxY, maxX):
    global debugStr
    boardX = game.boardOriginX
    boardY = game.boardOriginY
    drawBoard(stdscr, game, boardX, boardY)

    # Draw hero
    heroX = game.hero.x + game.boardOriginX
    heroY = game.hero.y + game.boardOriginY
    drawHero(stdscr, game, heroX, heroY)

    # Draw inventory
    inventoryX = 0
    inventoryY = game.boardOriginY
    displaySelector = game.mode == Modes.INVENTORY
    drawInventory(stdscr, game, game.hero.orderedInventory, "Inventory", inventoryX, inventoryY, displaySelector)


def draw(stdscr, game):
    global debugStr
    # TODO: What's practical difference between erase and clear?
    # Clears the current screen
    stdscr.erase()

    # resize if necessary
    maxY, maxX = resize(stdscr, game)

    # Draw any game messages
    for msg in game.messages:
        stdscr.addstr(0, game.boardOriginX, msg)
    game.messages = []

    # Draw game mode specific things
    if game.mode == Modes.PLAY or game.mode == Modes.INVENTORY:
        drawPlayMode(stdscr, game, maxY, maxX)
    
    # Draw debug panel
    stdscr.addstr(53, 0, debugStr)

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
    INVENTORY = 5
    EQUIP = 6
    ENTER = 7
    COOK = 8
    QUIT = 9

ActionMap = {
    curses.KEY_DOWN: Actions.DOWN,
    curses.KEY_UP: Actions.UP,
    curses.KEY_RIGHT: Actions.RIGHT,
    curses.KEY_LEFT: Actions.LEFT,
    10: Actions.ENTER,
    ord("c"): Actions.COOK,
    ord("i"): Actions.INVENTORY, # opens/closes inventory
    ord("q"): Actions.QUIT
}

def main(stdscr):
    global debugStr
    # Settings for nCurses
    curses.curs_set(False)
    initColors()

    # init random seed
    seed = 1557099878.4324212
    # seed = time.time()
    random.seed(seed)
    debugStr += str(seed) + " | "

    game = Game(stdscr, seed)

    # Game loop
    while True:
        draw(stdscr, game)
        hero = game.hero
        currBoard = game.boards[game.currBoardId]
        key = stdscr.getch()
        if key in ActionMap:
            # debugStr += str(key) + " "
            action = ActionMap[key]
            if action == Actions.QUIT:
                break
            if game.isGameOver == True:
                continue
            newHero = copy.deepcopy(game.hero)
            if game.mode == Modes.PLAY:
                game.changeGameMode(action, newHero)
                hero.move(game, action, newHero)
                hero.pickup(currBoard, action, newHero)
            elif game.mode == Modes.INVENTORY:
                game.changeGameMode(action, newHero)
                hero.moveSelection(game.hero.inventory, action, newHero)
            game.hero = newHero
            # draw(stdscr, game)




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

