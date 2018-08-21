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
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxwxxxxxxxxxxxxxxxx
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
        self.errorMsg = []

    def initGame(self):
        global debugStr
        # Initialize all boards.
        # TODO: Probably means this should be done in a for loop?
        board = Board()
        self.boards[board.id] = board
        self.hero = Hero()
    
    def toggle(self, action):
        global debugStr
        if action == Actions.TOGGLE:
            if self.mode == "play":
                self.mode = "inventory"
                self.hero.inventorySelectIdx = 0
            else:
                self.mode = "play"

#################################
# Board/Items
#################################
class Board:
    nextBoardId = 0
    def __init__(self):
        global debugStr
        self.id = self.nextBoardId
        Board.nextBoardId += 1
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
                    foo = BoardItem("weapon", "sword")
                    newRow.append(foo)
                elif cell == "a":
                    newRow.append(BoardItem("weapon", "axe"))
                elif cell == "b":
                    newRow.append(BoardItem("weapon", "bow"))
                elif cell == "m":
                    newRow.append(BoardItem("edible", "mushroom"))
                elif cell == "w":
                    newRow.append(BoardItem("armour", "waterboots"))
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
        BoardItem.boardItemNextId += 1
        self.mainType = mainType
        self.subType = subType

class ItemDefinition:
    def __init__(self, pos=None, dmg=0, defense=0, stealth=0, healing=0, mods=[]):
        self.pos = pos
        self.dmg = dmg
        self.defense = defense
        self.stealth = stealth
        self.healing = healing
        self.mods = mods

gameItems = {
    "sword": ItemDefinition(dmg=6, pos="hands"),
    "axe": ItemDefinition(dmg=8, pos="dualHands"),
    "spadone": ItemDefinition(dmg=8, pos="dualHands"),
    "bow": ItemDefinition(dmg=5, pos="hands"),
    "mushroom": ItemDefinition(mods=["stealth"]),
    "boots": ItemDefinition(defense=1, pos="feet"),
    "waterboots": ItemDefinition(pos="feet", mods=["waterwalking"]),
}

maxItemsPerPos = {
    "head": 1,
    "body": 1,
    "dualHands": 1,
    "hands": 2,
    "feet": 1,
}

#################################
# Board
#################################


class Hero:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.mods = []
        self.health = 100
        self.inventory = [] # []BoardItems
        self.inventorySelectIdx = -1
        self.equipMap = {
            "head": [],
            "body": [],
            "dualHands": [],
            "hands": [],
            "feet": [],
        } # map[pos]boardItem
    
    def move(self, mode, board, action):
        global debugStr
        if mode == "inventory":
            return
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
        global debugStr
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

    def pickup(self, mode, board):
        global debugStr
        if mode == "inventory":
            return
        # Check if there's an item at hero's x,y coordinates    
        boardItem = board.grid[self.y][self.x]
        # Pick up items
        if boardItem.mainType == "weapon" or boardItem.mainType == "edible" or boardItem.mainType == "armour":
            self.inventory.append(boardItem)
            board.grid[self.y][self.x] = BoardItem("terrain", "grass")

    def selectInventory(self, mode, action):
        global debugStr
        if mode == "play":
            return

        # Move selection down/up
        if action == Actions.DOWN:
            if self.inventorySelectIdx < len(self.inventory)-1:
                self.inventorySelectIdx += 1
        if action == Actions.UP:
            if self.inventorySelectIdx > 0:
                self.inventorySelectIdx -= 1

    # Only applicable for edibles (includes potions)
    def eat(self, mode, action):
        global debugStr
        if mode == "play":
            return
        # eat
        if action == Actions.ENTER:
            selectedItem = self.inventory[self.inventorySelectIdx] # BoardItem
            if selectedItem.mainType == "edible":
                # do something
                debugStr += "equip edible"
            
    # Equip hero with weapon or armour
    def equip(self, mode, action, errorMsg):
        global debugStr
        if mode == "play":
            return

        if action == Actions.ENTER:
            selectedItem = self.inventory[self.inventorySelectIdx] # BoardItem
            if selectedItem.mainType == "edible":
                return

            itemDefn = gameItems[selectedItem.subType]
            possibleEquipPos = itemDefn.pos

            # Dequip
            # Loop through list of items at possible equip position.
            for currItem in self.equipMap[possibleEquipPos]: # Also BoardItem
                # If item matches selected item, dequip
                if currItem == selectedItem:
                    self.equipMap[possibleEquipPos].remove(currItem)
                    for mod in itemDefn.mods:
                        self.mods.remove(mod)
                    debugStr += "dequip" + str(self.equipMap[possibleEquipPos])
                    return

            # Equip
            # None of items at possible equip position match current selected item. Equip
            numItemsAtEquipPos = len(self.equipMap[possibleEquipPos])
            # EquipPos Count already maxed out
            if numItemsAtEquipPos == maxItemsPerPos[possibleEquipPos]:
                errorStr = f"You can only have {maxItemsPerPos[possibleEquipPos]!r} items in {possibleEquipPos}"
                errorMsg.append(errorStr)
                debugStr += "Cannot equip. Too many already: " + str(self.equipMap[possibleEquipPos])
                return
            # Can't equip dualhanded weapon if already have a one handed weapon
            elif possibleEquipPos == "dualHands" and len(self.equipMap["hands"]) > 0:
                errorStr = f"This is a 2-handed item and you are already holding another item"
                errorMsg.append(errorStr)
                debugStr += "Cannot equp dualhands: " + str(self.equipMap[possibleEquipPos])
                return
            # Cannot equip any more hand weapons if already holding a dualhanded weapon
            elif possibleEquipPos == "hands" and len(self.equipMap["dualHands"]) == 1:
                errorStr = f"You don't have enough hands. Drop an item or make friends with an octopus!"
                errorMsg.append(errorStr)
                debugStr += "Cannot equp hands: " + str(self.equipMap[possibleEquipPos])
                return
            # Equip!
            else:
                self.equipMap[possibleEquipPos].append(selectedItem)
                for mod in itemDefn.mods:
                    self.mods.append(mod)
                debugStr += "equip: " + str(self.equipMap[possibleEquipPos])
                



#################################
# Paint
#################################
def draw(stdscr, game):
    global debugStr
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

    # Draw hero stats
    heroStatsY = game.boardOriginY
    heroStatsX = 175
    stdscr.addstr(heroStatsY, heroStatsX, "Hero Stats")
    heroStatsY += 1
    stdscr.addstr(heroStatsY, heroStatsX, "Health: " + str(game.hero.health))
    for mods in game.hero.mods:
        heroStatsY += 1
        stdscr.addstr(heroStatsY, heroStatsX, mods)

    # Draw inventory
    stdscr.addstr(game.boardOriginY, 0, "Inventory", curses.color_pair(Colors.INVENTORY))
    inventoryYIdx = game.boardOriginY+1
    inventory = game.hero.inventory
    for idx, item in enumerate(inventory):
        color = curses.color_pair(Colors.ITEMS)
        itemString = item.subType
        # Add asterik if item is selected
        if game.mode == "inventory":
            if idx == game.hero.inventorySelectIdx:
                itemString += " * "
        # Make item green if is equipped
        equippedPos = gameItems[item.subType].pos
        if equippedPos != None:
            for equippedItem in game.hero.equipMap[equippedPos]:
                if equippedItem.id == item.id:
                    color = curses.color_pair(Colors.GRASS)
        stdscr.addstr(inventoryYIdx, 0, itemString, color)
        inventoryYIdx += 1
    
    # Draw error messages
    for msg in game.errorMsg:
        stdscr.addstr(0, 15, msg)
    game.errorMsg = []

    # Draw debug panel
    global debugStr
    stdscr.addstr(45, 0, debugStr)

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
    TOGGLE = 5
    EQUIP = 6
    ENTER = 7   
    

actionMap = {
    curses.KEY_DOWN: Actions.DOWN,
    curses.KEY_UP: Actions.UP,
    curses.KEY_RIGHT: Actions.RIGHT,
    curses.KEY_LEFT: Actions.LEFT,
    9: Actions.TOGGLE,
    10: Actions.ENTER,
}

def main(stdscr):
    global debugStr
    game = Game()
    game.initGame()
    currBoard = game.boards[game.currBoardId]
    hero = game.hero

    # Settings for nCurses
    curses.curs_set(False)
    initColors()

    # Game loop
    while True:
        draw(stdscr, game)
        key = stdscr.getch()
        if key == ord("q"):
            break
        if key in actionMap:
            action = actionMap[key]
            game.toggle(action)
            hero.move(game.mode, currBoard, action)
            # Hero should pick up items regardless of what action is being taken
            hero.pickup(game.mode, currBoard)
            hero.selectInventory(game.mode, action)
            hero.eat(game.mode, action)
            hero.equip(game.mode, action, game.errorMsg)


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

