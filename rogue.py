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
        self.boardOriginX = None
        self.boardOriginY = None
        self.messages = []
        # self.selectedItemIdx = 0
        # self.removeSelectedInventoryItem = False

    def initGame(self):
        global debugStr
        # Initialize all boards.
        # TODO: Probably means this should be done in a for loop?
        board = Board()
        self.boards[board.id] = board
        self.hero = Hero()
    
    def changeGameMode(self, action):
        global debugStr
        if action == Actions.TOGGLE and self.mode != "cook":
            self.hero.selectedItemIdx = 0
            if self.mode == "play":
                self.mode = "inventory"
            elif self.mode == "inventory":
                self.mode = "play"
        if action == Actions.COOK:
            self.hero.selectedItemIdx = 0
            if self.mode == "cook":
                self.hero.addUncookedItemsBack()
                self.mode = "play"
            else:
                self.mode = "cook"

            

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
    def __init__(self, equipPos=None, dmg=0, defense=0, stealth=0, healing=0, mods=[]):
        self.equipPos = equipPos
        self.dmg = dmg # Hero or monster health
        self.defense = defense # Hero or monster defense
        self.healing = healing # Hero health
        self.mods = mods # Hero mods

gameItemDefns = {
    "sword": ItemDefinition(dmg=6, equipPos="hands"),
    "axe": ItemDefinition(dmg=8, equipPos="dualHands"),
    "spadone": ItemDefinition(dmg=8, equipPos="dualHands"),
    "bow": ItemDefinition(dmg=5, equipPos="hands"),
    "mushroom": ItemDefinition(mods=["stealth"]),
    "boots": ItemDefinition(defense=1, equipPos="feet"),
    "waterboots": ItemDefinition(equipPos="feet", mods=["waterwalking"]),
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
        self.mods = set()
        self.health = 100
        self.inventory = [] # []BoardItems
        self.pot = []
        self.cookState = "inventory"
        self.selectedItemIdx = 0
        self.shouldRemoveSelectedItem = False
        self.equipMap = {
            "head": [],
            "body": [],
            "dualHands": [],
            "hands": [],
            "feet": [],
        } # map[pos]boardItem
    
    def move(self, mode, board, action):
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
        
        # Check bounds and if move into next cell?
        if newX >= 0 and newX < board.width and newY >= 0 and newY < board.height:
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

        # Check if there's an item at hero's x,y coordinates    
        boardItem = board.grid[self.y][self.x]
        # Pick up items
        if boardItem.mainType == "weapon" or boardItem.mainType == "edible" or boardItem.mainType == "armour":
            self.inventory.append(boardItem)
            board.grid[self.y][self.x] = BoardItem("terrain", "grass")

    def selectItem(self, itemList, action):
        global debugStr

        # Move selection down/up
        if action == Actions.DOWN:
            if self.selectedItemIdx < len(itemList)-1:
                self.selectedItemIdx += 1
        if action == Actions.UP:
            if self.selectedItemIdx > 0:
                self.selectedItemIdx -= 1

    def removeSelectedInventoryItem(self, itemList):
        if self.shouldRemoveSelectedItem == True:
            del itemList[self.selectedItemIdx]
            if self.selectedItemIdx > 0:
                self.selectedItemIdx -= 1
        self.shouldRemoveSelectedItem = False


    def cook(self, action):
        global debugStr
        # Pick which list to arrow through
        if action == Actions.LEFT:
            if self.cookState == "cook":
                self.selectedItemIdx = 0
                self.cookState = "pot"
            elif self.cookState == "pot":
                self.selectedItemIdx = 0
                self.cookState = "inventory"
        elif action == Actions.RIGHT:
            if self.cookState == "inventory":
                self.selectedItemIdx = 0
                self.cookState = "pot"
            elif self.cookState == "pot":
                self.selectedItemIdx = 0
                self.cookState = "cook"

        # Arrow through selected list
        if self.cookState == "pot":
            self.selectItem(self.pot, action)
        elif self.cookState == "inventory":
            self.selectItem(self.inventory, action)

        # Either add or remove item from pot
        if action == Actions.ENTER:
            if self.cookState == "inventory":
                self.pot.append(self.inventory[self.selectedItemIdx])
                self.shouldRemoveSelectedItem = True
                self.removeSelectedInventoryItem(self.inventory)
            elif self.cookState == "pot":
                self.inventory.append(self.pot[self.selectedItemIdx])
                self.shouldRemoveSelectedItem = True
                self.removeSelectedInventoryItem(self.pot)
            elif self.cookState == "cook":
                # self.inventory.append(BoardItem("potion", "potion"))
                # self.pot = []
                # do something
                debugStr += " Create new item to add to inventory"
                
    
    def addUncookedItemsBack(self):
        for item in self.pot:
            self.inventory.append(item)
        self.pot = []


    # Only applicable for edibles
    def eat(self, game, action):
        global debugStr

        # eat
        if action == Actions.ENTER:
            selectedItem = self.inventory[self.selectedItemIdx] # BoardItem
            if selectedItem.mainType == "edible":
                itemDefn = gameItemDefns[selectedItem.subType]
                # Apply dmg, if any
                self.health -= itemDefn.dmg
                # Apply healing, if any
                self.health += itemDefn.healing
                # Apply mods, if any
                for mod in itemDefn.mods:
                    self.mods.add(mod)
                self.shouldRemoveSelectedItem = True
                
            
    # Equip hero with weapon or armour
    def equip(self, game, action):
        global debugStr

        if action == Actions.ENTER:
            selectedItem = self.inventory[self.selectedItemIdx] # BoardItem
            if selectedItem.mainType == "weapon" or selectedItem.mainType == "armour":
                itemDefn = gameItemDefns[selectedItem.subType]
                possibleEquipPos = itemDefn.equipPos

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
                    game.messages.append(errorStr)
                    debugStr += "Cannot equip. Too many already: " + str(self.equipMap[possibleEquipPos])
                    return
                # Can't equip dualhanded weapon if already have a one handed weapon
                elif possibleEquipPos == "dualHands" and len(self.equipMap["hands"]) > 0:
                    errorStr = f"This is a 2-handed item and you are already holding another item"
                    game.messages.append(errorStr)
                    debugStr += "Cannot equp dualhands: " + str(self.equipMap[possibleEquipPos])
                    return
                # Cannot equip any more hand weapons if already holding a dualhanded weapon
                elif possibleEquipPos == "hands" and len(self.equipMap["dualHands"]) == 1:
                    errorStr = f"You don't have enough hands. Drop an item or make friends with an octopus!"
                    game.messages.append(errorStr)
                    debugStr += "Cannot equp hands: " + str(self.equipMap[possibleEquipPos])
                    return
                # Equip!
                else:
                    self.equipMap[possibleEquipPos].append(selectedItem)
                    for mod in itemDefn.mods:
                        self.mods.add(mod)
                    debugStr += "equip: " + str(self.equipMap[possibleEquipPos])

                    



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

def drawInventory(stdscr, game, posX, posY):
    global debugStr
    stdscr.addstr(posY, posX, "Inventory", curses.color_pair(Colors.INVENTORY))
    posY += 1
    inventory = game.hero.inventory
    for idx, item in enumerate(inventory):
        color = curses.color_pair(Colors.ITEMS)
        itemString = item.subType
        # Add asterik if item is selected
        if idx == game.hero.selectedItemIdx and (game.hero.cookState != "pot" and game.hero.cookState != "cook"):
            itemString += " * "
        # Make item green if is equipped
        equippedPos = gameItemDefns[item.subType].equipPos
        if equippedPos != None:
            for equippedItem in game.hero.equipMap[equippedPos]:
                if equippedItem.id == item.id:
                    color = curses.color_pair(Colors.GRASS)
        stdscr.addstr(posY, posX, itemString, color)
        posY += 1

def drawBoard(stdscr, game, boardX, boardY):
    board = game.boards[game.currBoardId].grid
    for j, row in enumerate(board):
        for i, cell in enumerate(row):
            x = boardX + i
            y = boardY + j
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

def drawHero(stdscr, game, heroX, heroY):
    stdscr.addstr(heroY, heroX, "h", curses.color_pair(Colors.HERO))

def drawHeroStats(stdscr, game, heroStatsX, heroStatsY, maxY, maxX):
    heroStatsX = maxX - 20
    heroStatsY = game.boardOriginY
    stdscr.addstr(heroStatsY, heroStatsX, "Hero Stats")
    heroStatsY += 1
    stdscr.addstr(heroStatsY, heroStatsX, "Health: " + str(game.hero.health))
    for mods in game.hero.mods:
        heroStatsY += 1
        stdscr.addstr(heroStatsY, heroStatsX, mods)

def drawCookMode(stdscr, game):
    inventoryX = game.boardOriginX
    inventoryY = game.boardOriginY
    drawInventory(stdscr, game, inventoryX, inventoryY)

    potX = game.boardOriginX + 30
    potY = game.boardOriginY
    stdscr.addstr(potY, potX, "Pot", curses.color_pair(Colors.INVENTORY))
    potY += 1
    for idx, item in enumerate(game.hero.pot):
        color = curses.color_pair(Colors.ITEMS)
        itemString = item.subType
        if idx == game.hero.selectedItemIdx and game.hero.cookState == "pot":
            itemString += " * "
        stdscr.addstr(potY, potX, itemString, color)
        potY += 1

    # Cook
    cookString = "Cook?"
    if game.hero.cookState == "cook":
        cookString += " * "
    stdscr.addstr(game.boardOriginY, potX + 30, cookString, curses.color_pair(Colors.INVENTORY))


def drawPlayMode(stdscr, game, maxY, maxX):
    boardX = game.boardOriginX
    boardY = game.boardOriginY
    drawBoard(stdscr, game, boardX, boardY)

    # Draw hero
    heroX = game.hero.x + game.boardOriginX
    heroY = game.hero.y + game.boardOriginY
    drawHero(stdscr, game, heroX, heroY)

    # Draw hero stats
    heroStatsX = maxX - 20
    heroStatsY = game.boardOriginY
    drawHeroStats(stdscr, game, heroStatsX, heroStatsY, maxY, maxX)

    # Draw inventory
    inventoryX = 0
    inventoryY = game.boardOriginY
    drawInventory(stdscr, game, inventoryX, inventoryY)

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
    if game.mode == "cook":
        drawCookMode(stdscr, game)
    elif game.mode == "play" or game.mode == "inventory":
        drawPlayMode(stdscr, game, maxY, maxX)
    
    # Draw debug panel
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
    COOK = 8
    

actionMap = {
    curses.KEY_DOWN: Actions.DOWN,
    curses.KEY_UP: Actions.UP,
    curses.KEY_RIGHT: Actions.RIGHT,
    curses.KEY_LEFT: Actions.LEFT,
    9: Actions.TOGGLE,
    10: Actions.ENTER,
    ord("c"): Actions.COOK
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
            game.changeGameMode(action)
            if game.mode == "play":
                hero.move(game.mode, currBoard, action)
                # Hero should pick up items regardless of what action is being taken
                hero.pickup(game.mode, currBoard)
            if game.mode == "inventory":
                hero.selectItem(game.hero.inventory, action)
                hero.eat(game, action)
                hero.equip(game, action)
                hero.removeSelectedInventoryItem(game.hero.inventory)
            if game.mode == "cook":
                hero.cook(action)
            


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

