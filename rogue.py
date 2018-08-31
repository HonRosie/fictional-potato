import copy
import curses
import random
from curses import wrapper
from enum import Enum, IntEnum


mainBoard = """xsxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xsxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xaxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xbxxxxxxxx-----xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxsxxxxxxxxx
xxxxxxuxxxxxx*****xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxx***xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxx***xxxxxxxxxxxxxxxxxxxsxxxxxxxxx
xxxxxxxxxxxxxxxxxxx***xxxxxxxxxxxxxxxoxxxxxxxxxxxx
xxxxxxxxxmxxxxxxxxxx***xxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxx**xxxxxxx--------xxxxxxxxxxxx
xxxxxxx@xxxxxxxxxxxxxx*xxxxxxxxxxxxxx-xxxxxxxxxxxx
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
class Modes(Enum):
    PLAY = 1
    INVENTORY = 2
    COOK = 3

class Game:
    def __init__(self):
        self.mode = Modes.PLAY
        self.hero = Hero()
        self.boards = {}
        self.currBoardId = 0
        self.boardOriginX = None
        self.boardOriginY = None
        self.messages = []
        # self.selectedItemIdx = 0

    def initGame(self):
        global debugStr
        # Initialize all boards.
        # TODO: Probably means this should be done in a for loop?
        board = Board()
        self.boards[board.id] = board
        self.hero = Hero()
    
    # def changeGameMode(self, action):
    #     global debugStr
    #     if action == Actions.TOGGLE and self.mode != "cook":
    #         self.hero.selectedItemIdx = 0
    #         if self.mode == "play":
    #             self.mode = "inventory"
    #         elif self.mode == "inventory":
    #             self.mode = "play"
    #     if action == Actions.COOK:
    #         self.hero.selectedItemIdx = 0
    #         if self.mode == "cook":
    #             self.hero.addUncookedItemsBack()
    #             self.mode = "play"
    #         else:
    #             self.mode = "cook"

    def changeModeFromPlay(self, action, newHero):
        global debugStr
        if action == Actions.TOGGLE:
            newHero.selectedItemIdx = 0
            self.mode = Modes.INVENTORY
        if action == Actions.COOK:
            newHero.selectedItemIdx = 0
            self.mode = Modes.COOK

    def changeModeFromInventory(self, action, newHero):
        global debugStr
        if action == Actions.TOGGLE:
            newHero.selectedItemIdx = 0
            self.mode = Modes.PLAY
        if action == Actions.COOK:
            newHero.selectedItemIdx = 0
            self.mode = Modes.COOK

    def changeModeFromCook(self, action, newHero):
        global debugStr
        if action == Actions.COOK:
            self.mode = Modes.PLAY



            

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
        self.currMonster = None # Item Definition

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
                elif cell == "u":
                    newRow.append(BoardItem("monster", "uruk-hai"))
                elif cell == "o":
                    newRow.append(BoardItem("monster", "orc"))
                elif cell == "@":
                    newRow.append(BoardItem("armour", "basic armour"))
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
    def __init__(self, equipPos=None, dmg=0, defense=0, stealth=0, healing=0, mods=[], health=0):
        self.equipPos = equipPos
        self.dmg = dmg # Hero or monster dmg
        self.defense = defense # Hero or monster defense
        self.healing = healing # Hero health
        self.mods = mods # Hero mods
        self.health = health # monster health

gameItemDefns = {
    "sword": ItemDefinition(dmg=6, equipPos="hands"),
    "axe": ItemDefinition(dmg=8, equipPos="dualHands"),
    "spadone": ItemDefinition(dmg=8, equipPos="dualHands"),
    "bow": ItemDefinition(dmg=5, equipPos="hands"),
    "mushroom": ItemDefinition(mods=["stealth"]),
    "boots": ItemDefinition(defense=1, equipPos="feet"),
    "waterboots": ItemDefinition(equipPos="feet", mods=["waterwalking"]),
    "basic armour": ItemDefinition(defense=2, equipPos="body"),
    "uruk-hai": ItemDefinition(dmg=12, defense=3, health=30),
    "orc": ItemDefinition(dmg=8, defense=3, health=20)
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
        self.equipMap = {
            "head": [],
            "body": [],
            "dualHands": [],
            "hands": [],
            "feet": [],
        } # map[pos]boardItem
        self.inventory = [] # []BoardItems
        self.pot = []
        self.cookState = "inventory"
        self.selectedItemIdx = 0
        self.shouldRemoveSelectedItem = False


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

    def move(self, board, action, newHero):
        global debugStr
        newX, newY = self.computeNewPos(board, action, False)
        
        newHero.x = newX
        newHero.y = newY

            
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
        if boardItemType == "terrain" or boardItemType == "monster":
            return True
        
        # Default to not blocked
        return False

    def pickup(self, board, action, newHero):
        global debugStr
        newX, newY = self.computeNewPos(board, action, False)
        # Check if there's an item at hero's x,y coordinates    
        boardItem = board.grid[newY][newX]
        # Pick up items
        if boardItem.mainType == "weapon" or boardItem.mainType == "edible" or boardItem.mainType == "armour":
            newHero.inventory.append(boardItem)
            board.grid[newY][newX] = BoardItem("terrain", "grass")

    def combat(self, game, board, action, newHero):
        global debugStr

        newX, newY = self.computeNewPos(board, action, True)
        boardItem = board.grid[newY][newX]

        if boardItem.mainType == "monster":
            if board.currMonster == None:
                debugStr += "foo"
                board.currMonster = {
                    "monsterId": boardItem.id
                }
                # Calculate dmg of monster
                monsterDefn = gameItemDefns[boardItem.subType]
                board.currMonster["dmg"] = monsterDefn.dmg
                board.currMonster["defense"] = monsterDefn.defense
                board.currMonster["health"] = monsterDefn.health
            
            monster = board.currMonster

            # Calculate dmg of hero
            heroDmg, heroDefense = 0, 0
            for pos, itemList in self.equipMap.items():
                for item in itemList:
                    itemDefn = gameItemDefns[item.subType]
                    heroDmg += itemDefn.dmg
                    heroDefense += itemDefn.defense

            # inflict dmg
            heroFinalDmg = heroDmg * (1 - monster["defense"]/100)
            monsterFinalDmg = monster["dmg"] * (1 - heroDefense/100)

            newHero.health -= monsterFinalDmg
            monster["health"] -= heroFinalDmg

            if monster["health"] <= 0:
                message = f"Successful beat {boardItem.subType}!!"
                game.messages.append(message)
                board.grid[newY][newX] = BoardItem("terrain", "grass")
                board.currMonster = None


    def chanceOfDmg(self, defense):
        randomNum = random.randrange(100)
        return randomNum > defense


    def moveSelection(self, itemList, action, newHero):
        global debugStr
        # Move selection down/up
        if action == Actions.DOWN:
            if self.selectedItemIdx < len(itemList)-1:
                newHero.selectedItemIdx += 1
        if action == Actions.UP:
            if self.selectedItemIdx > 0:
                newHero.selectedItemIdx -= 1

    def removeSelectedItem(self, itemList, newHero):
        # TODO Is it okay to assume order is the same across deep copy?
        del itemList[newHero.selectedItemIdx]
        if self.selectedItemIdx > 0:
            newHero.selectedItemIdx -= 1


    def cook(self, action, newHero):
        global debugStr
        # Pick which list to arrow through
        if action == Actions.LEFT:
            newHero.selectedItemIdx = 0
            if self.cookState == "cook":
                if len(self.pot) != 0:
                    newHero.cookState = "pot"
                else:
                    newHero.cookState = "inventory"
            elif self.cookState == "pot":
                newHero.cookState = "inventory"
        elif action == Actions.RIGHT:
            newHero.selectedItemIdx = 0
            if self.cookState == "inventory" and len(self.pot) != 0:
                newHero.cookState = "pot"
            elif self.cookState == "pot":
                newHero.cookState = "cook"

        # Arrow through selected list
        if self.cookState == "pot":
            self.moveSelection(self.pot, action, newHero)
        elif self.cookState == "inventory":
            self.moveSelection(self.inventory, action, newHero)

        # Either add or remove item from pot
        if action == Actions.ENTER:
            if self.cookState == "inventory":
                newHero.pot.append(self.inventory[self.selectedItemIdx])
                self.removeSelectedItem(newHero.inventory, newHero)
            elif self.cookState == "pot":
                newHero.inventory.append(self.pot[self.selectedItemIdx])
                self.removeSelectedItem(newHero.pot, newHero)
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
    def eat(self, game, action, newHero):
        global debugStr
        # eat
        if action == Actions.ENTER:
            selectedItem = self.inventory[self.selectedItemIdx] # BoardItem
            if selectedItem.mainType == "edible":
                itemDefn = gameItemDefns[selectedItem.subType]
                # Apply dmg, if any
                newHero.health -= itemDefn.dmg
                # Apply healing, if any
                newHero.health += itemDefn.healing
                # Apply mods, if any
                for mod in itemDefn.mods:
                    newHero.mods.add(mod)
                self.removeSelectedItem(newHero.inventory, newHero)
                
            
    # Equip hero with weapon or armour
    def equip(self, game, action, newHero):
        global debugStr

        if action == Actions.ENTER:
            selectedItem = self.inventory[self.selectedItemIdx] # BoardItem
            if selectedItem.mainType == "weapon" or selectedItem.mainType == "armour":
                itemDefn = gameItemDefns[selectedItem.subType]
                possibleEquipPos = itemDefn.equipPos

                # Dequip
                # Loop through list of items at possible equip position.
                for idx, currItem in enumerate(self.equipMap[possibleEquipPos]): # Also BoardItem
                    # If item matches selected item, dequip. Comparison by object no longer works
                    # TODO: Suspicion is even though when addied, is adding same item from inventory to equipMap.
                    # However, during deep copy, copies of inventory and equipMap are made, where the items no
                    # longer reference each other
                    # ie. "foo" from inventory() is added to equipMap so it also has "foo".
                    # During deep copy, "foo" in inventory becomes "foo1", and "foo" in equipMap becomes "foo2"?
                    if currItem.id == selectedItem.id:
                        # TODO: Should this instead be a loop which removes the correct id?
                        del newHero.equipMap[possibleEquipPos][idx]
                        for mod in itemDefn.mods:
                            newHero.mods.remove(mod)
                        # debugStr += "dequip" + str(newHero.equipMap[possibleEquipPos])
                        return

                # Equip
                # None of items at possible equip position match current selected item. Equip
                numItemsAtEquipPos = len(self.equipMap[possibleEquipPos])
                # EquipPos Count already maxed out
                if numItemsAtEquipPos == maxItemsPerPos[possibleEquipPos]:
                    errorStr = f"You can only have {maxItemsPerPos[possibleEquipPos]!r} items in {possibleEquipPos}"
                    game.messages.append(errorStr)
                    # debugStr += "Too many already: " + str(self.equipMap[possibleEquipPos])
                    return
                # Can't equip dualhanded weapon if already have a one handed weapon
                elif possibleEquipPos == "dualHands" and len(self.equipMap["hands"]) > 0:
                    errorStr = f"This is a 2-handed item and you are already holding another item"
                    game.messages.append(errorStr)
                    # debugStr += "Cannot equp dualhands: " + str(self.equipMap[possibleEquipPos])
                    return
                # Cannot equip any more hand weapons if already holding a dualhanded weapon
                elif possibleEquipPos == "hands" and len(self.equipMap["dualHands"]) == 1:
                    errorStr = f"You don't have enough hands. Drop an item or make friends with an octopus!"
                    game.messages.append(errorStr)
                    # debugStr += "Cannot equp hands: " + str(self.equipMap[possibleEquipPos])
                    return
                # Equip!
                else:
                    newHero.equipMap[possibleEquipPos].append(selectedItem)
                    for mod in itemDefn.mods:
                        newHero.mods.add(mod)
                    # debugStr += "equip: " + str(newHero.equipMap[possibleEquipPos])

                    



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

def drawList(stdscr, game, itemList, title, posX, posY, displaySelector):
    global debugStr
    stdscr.addstr(posY, posX, title, curses.color_pair(Colors.INVENTORY))
    posY += 1
    for idx, item in enumerate(itemList):
        color = curses.color_pair(Colors.ITEMS)
        itemString = item.subType
        # Add asterik if item is selected
        if idx == game.hero.selectedItemIdx and displaySelector:
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
            elif cell.subType == "uruk-hai":
                stdscr.addstr(y, x, "u", curses.color_pair(Colors.ITEMS))
            elif cell.subType == "orc":
                stdscr.addstr(y, x, "o", curses.color_pair(Colors.ITEMS))
            elif cell.subType == "basic armour":
                stdscr.addstr(y, x, "@", curses.color_pair(Colors.ITEMS))
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
    heroDmg, heroDefense = 0, 0
    for pos, itemList in game.hero.equipMap.items():
        for item in itemList:
            itemDefn = gameItemDefns[item.subType]
            heroDmg += itemDefn.dmg
            heroDefense += itemDefn.defense
    heroStatsY += 1                
    stdscr.addstr(heroStatsY, heroStatsX, "Damage: " + str(heroDmg))
    heroStatsY += 1
    stdscr.addstr(heroStatsY, heroStatsX, "Defense: " + str(heroDefense))
    for mods in game.hero.mods:
        heroStatsY += 1
        stdscr.addstr(heroStatsY, heroStatsX, mods)

def drawCookMode(stdscr, game):
    inventoryX = game.boardOriginX
    inventoryY = game.boardOriginY
    displaySelector = game.hero.cookState == "inventory"
    drawList(stdscr, game, game.hero.inventory, "Inventory", inventoryX, inventoryY, displaySelector)

    potX = game.boardOriginX + 30
    potY = game.boardOriginY
    displaySelector = game.hero.cookState == "pot"
    drawList(stdscr, game, game.hero.pot, "Pot", potX, potY, displaySelector)

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
    displaySelector = game.mode == Modes.INVENTORY
    drawList(stdscr, game, game.hero.inventory, "Inventory", inventoryX, inventoryY, displaySelector)

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
    if game.mode == Modes.COOK:
        drawCookMode(stdscr, game)
    elif game.mode == Modes.PLAY or game.mode == Modes.INVENTORY:
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
    QUIT = 9
    

ActionMap = {
    curses.KEY_DOWN: Actions.DOWN,
    curses.KEY_UP: Actions.UP,
    curses.KEY_RIGHT: Actions.RIGHT,
    curses.KEY_LEFT: Actions.LEFT,
    9: Actions.TOGGLE,
    10: Actions.ENTER,
    ord("c"): Actions.COOK,
    ord("q"): Actions.QUIT
}



def main(stdscr):
    global debugStr
    game = Game()
    game.initGame()
    currBoard = game.boards[game.currBoardId]
    

    # Settings for nCurses
    curses.curs_set(False)
    initColors()

    # Game loop
    while True:
        hero = game.hero
        draw(stdscr, game)
        key = stdscr.getch()
        if key in ActionMap:
            action = ActionMap[key]
            if action == Actions.QUIT:
                break
            newHero = copy.deepcopy(game.hero)
            if game.mode == Modes.PLAY:
                game.changeModeFromPlay(action, newHero)
                hero.move(currBoard, action, newHero)
                # Hero should pick up items regardless of what action is being taken
                hero.pickup(currBoard,action, newHero)
                hero.combat(game, currBoard, action, newHero)
            elif game.mode == Modes.INVENTORY:
                game.changeModeFromInventory(action, newHero)
                hero.moveSelection(game.hero.inventory, action, newHero)
                hero.eat(game, action, newHero)
                hero.equip(game, action, newHero)
                # hero.removeSelectedItem(game.hero.inventory, newHero)
            elif game.mode == Modes.COOK:
                game.changeModeFromCook(action, newHero)
                hero.cook(action, newHero)
            game.hero = newHero




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

