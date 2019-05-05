import copy
import curses
import random
import time
from enum import Enum, IntEnum
from boardCell import BoardCell

debugStr = ""

MAXWIDTH = 180
MAXHEIGHT = 45

class Direction(Enum):
    TOP = 1
    BOTTOM = 2
    LEFT = 3
    RIGHT = 4

flipDirectionDict = {
    Direction.TOP: Direction.BOTTOM,
    Direction.BOTTOM: Direction.TOP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,    
}

def generateRooms(stdscr, seed):
    global debugStr
    # init random number generator
    random.seed(seed)

    numRooms = 19
    grid = []
    roomList = []
    # init grid
    for y in range(MAXHEIGHT):
        newRow = []
        for x in range(MAXWIDTH):
            newRow.append(BoardCell("background", "background"))
        grid.append(newRow)

    # init first room
    prevRoom = ComplexRoom()
    # debugStr += str(prevRoom.height) + "," + str(prevRoom.width)
    middleX, middleY = getTopLeftForStartingRoom(stdscr, prevRoom)
    # debugStr += " TopLeft: " + str(middleX) + "," + str(middleY)
    prevRoom.setPosition(middleX, middleY)
    roomList.append(prevRoom)
    miniGrid = copyRoomToMiniGrid(prevRoom)
    smoothedMiniGrid = smoothMiniGrid(miniGrid)
    copyRoomToGrid(prevRoom, smoothedMiniGrid, grid)

    for i in range(numRooms):
        createRoomSuccess = False
        baseRoomAttempts = 0
        while baseRoomAttempts < 10 and createRoomSuccess == False:
            prevRoom = random.choice(roomList)
            numAttempts = 0
            while numAttempts < 5:
                room = ComplexRoom()
                # debugStr += " New:" + str(room.height) + "," + str(room.width)
                direction = pickDirection()
                # debugStr += " " + str(direction)
                room.centerOnSide(direction, prevRoom)
                shiftEdgesToOverlap(prevRoom, room, direction)
                isClear = isAreaClear(roomList, room)
                onGrid = isOnGrid(room)
                # debugStr += " Clear: " + str(isClear) + " |||||| "
                if isClear and onGrid:
                    # debugStr += " Creating door"
                    start, end = getSharedEdge(prevRoom, room, direction)
                    start, end = getSharedInnerEdge(start, end)
                    door = createDoorFromAToB(start, end, prevRoom, room, direction) # TODO should create on both room?
                    roomList.append(room)
                    miniGrid = copyRoomToMiniGrid(room)
                    smoothedMiniGrid = smoothMiniGrid(miniGrid)
                    copyRoomToGrid(room, smoothedMiniGrid, grid)
                    createRoomSuccess = True
                    break
                numAttempts += 1
            baseRoomAttempts += 1

    # room = ComplexRoom()
    # room.setPosition(0,0)
    # roomList.append(room)

    # for each room, set the door to be type door BoardCell in grid
    setDoorsOnBoard(roomList, grid)
    # return (grid, newGrid)
    return (grid, roomList)


#############################################
# Copy room to grid with smoothing
#############################################
# Copies room to a mini grid and sets cells with appropriate terrain
def copyRoomToMiniGrid(room):
    global debugStr
    miniGrid = []
    for y in range(room.height):
        newRow = []
        for x in range(room.width):
            newRow.append(BoardCell("background", "background"))
        miniGrid.append(newRow)
    try:
        for rectangle in room.rectangleList:
            # draws top and bottom walls
            for y in [rectangle.top, rectangle.bottom]:
                for x in range(rectangle.left, rectangle.right+1):
                    if not miniGrid[y][x].subType == "grass":
                        miniGrid[y][x] = BoardCell("terrain", "wall")
            # draws right and left walls
            for y in range(rectangle.top, rectangle.bottom+1):
                for x in [rectangle.left, rectangle.right]:
                    if not miniGrid[y][x].subType == "grass":
                        miniGrid[y][x] = BoardCell("terrain", "wall")
            # fills in with terrain
            for y in range(rectangle.top+1, rectangle.bottom):
                for x in range(rectangle.left+1, rectangle.right):
                    miniGrid[y][x] = BoardCell("terrain", "grass")
    except:
        raise ValueError(room.width, room.height, x, y, foo)
    return miniGrid

# remove internal walls
def smoothMiniGrid(miniGrid):
    global debugStr
    height = len(miniGrid)
    width = len(miniGrid[0])
    #TODO I don't think having a new grid is necessary?
    newGrid = copy.deepcopy(miniGrid)
    for y in range(height):
        for x in range(width):
            if miniGrid[y][x].subType == "wall":
                # If is on edge of entire board, must be outer wall
                if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                    continue
                openCount = getNeighbourOpenCount(x, y, miniGrid)
                if openCount < 1:
                    newGrid[y][x] = BoardCell("terrain", "grass")
    miniGrid = newGrid
    return miniGrid

# counts the number of "background" type neighbors for x, y
def getNeighbourOpenCount(x, y, grid):
    openCount = 0
    for j in [-1, 0, 1]:
        for i in [-1, 0, 1]:
            newX = x + i
            newY = y + j
            if newX < 0 or newX >= len(grid[0]) or newY < 0 or newY >= len(grid):
                continue
            if newX == x and newY == y:
                continue
            if grid[newY][newX].mainType == "background":
                openCount += 1
    return openCount

# copies mini room to larger grid
def copyRoomToGrid(room, miniGrid, grid):
    global debugStr
    xOffset = room.left
    yOffset = room.top
    try:
        for y in range(len(miniGrid)):
            for x in range(len(miniGrid[0])):
                # don't draw background of mini-grid
                if miniGrid[y][x].mainType == "background":
                    continue
                globalX = x + xOffset
                globalY = y + yOffset
                grid[globalY][globalX] = miniGrid[y][x]
    except:
        raise ValueError(x, y, xOffset, yOffset, globalX, globalY)

def setDoorsOnBoard(roomList, grid):
    for room in roomList:
        for door in room.doors:
            grid[door[1]][door[0]] = BoardCell("door", "unlocked")


# Figures out the top left corner for prevRoom centered in the middle of the screen
def getTopLeftForStartingRoom(stdscr, prevRoom):
    global debugStr
    # maxY, maxX = stdscr.getmaxyx()
    # curses.resizeterm(maxY, maxX)
    middleY = MAXHEIGHT/2
    middleTopLeftY = int(middleY - prevRoom.height/2)
    middleX = MAXWIDTH/2
    middleTopLeftX = int(middleX - prevRoom.width/2)
    return (middleTopLeftX, middleTopLeftY)

def pickDirection():
    # top, bottom, left, right
    directions = list(Direction)
    weight = [0.25, 0.25, 0.25, 0.25]
    choiceList = random.choices(directions, weight, k=1)
    return choiceList[0]

# Checks if two ranges intersect
# isSharedWallIntersection: True if should count shared wall as intersection
def isRangeIntersect(start1, end1, start2, end2, isSharedWallIntersection):
    global debugStr
    if isSharedWallIntersection:
        if start1 <= end2 and end1 >= start2:
            # debugStr += " (" + str(start1) + "," + str(end1) + "::" + str(start2) + "," + str(end2) + ") "
            return True
    else:
        if start1 < end2 and end1 > start2:
            # debugStr += " (" + str(start1) + "," + str(end1) + "::" + str(start2) + "," + str(end2) + ") "
            return True
    return False


def getSharedEdge(roomA, roomB, direction):
    global debugStr
    edgeA = roomA.getEdge(direction)
    # debugStr += "A: " + str(edgeA) + ", "
    edgeB = roomB.getEdge(flipDirectionDict[direction])
    # debugStr += "B: " + str(edgeB) + ":: "
    if isRangeIntersect(edgeA[0], edgeA[1], edgeB[0], edgeB[1], True):
        # debugStr += str((max(edgeA[0], edgeB[0]), min(edgeA[1], edgeB[1])))
        return (max(edgeA[0], edgeB[0]), min(edgeA[1], edgeB[1]))
    else:
        return (None, None)

def getSharedInnerEdge(start, end):
    return (start+1, end-1)


def shiftEdgesToOverlap(roomA, roomB, direction):
    global debugStr
    edgeA = roomA.getEdge(direction)
    edgeB = roomB.getEdge(flipDirectionDict[direction])
    minOverlap = 3
    maxOverlap = min(getLengthOfEdge(edgeA), getLengthOfEdge(edgeB))
    overlap = random.randint(minOverlap, maxOverlap)
    # debugStr += " overlap: " + str(overlap)

    # Figure out offset
    if edgeA[1] < edgeB[0]: # shift B up or left
        newEdgeBStart = edgeA[1] - (overlap-1)
        shiftOffset = newEdgeBStart - edgeB[0]
    else: # shift B down or right
        newEdgeBEnd = edgeA[0] + (overlap-1)
        shiftOffset = newEdgeBEnd - edgeB[1]
    # debugStr += " offset: " + str(shiftOffset)

    # Move room
    if direction == Direction.TOP or direction == Direction.BOTTOM:
        # sets roomB left or right
        x = roomB.left + shiftOffset
        roomB.setPosition(x, roomB.top)
    if direction == Direction.LEFT or direction == Direction.RIGHT:
        # shift roomB up or down
        y = roomB.top + shiftOffset
        roomB.setPosition(roomB.left, y)

    # newEdgeA = roomA.getEdge(direction)
    # newEdgeB = roomB.getEdge(direction)
    # debugStr += str(edgeA) + "," + str(newEdgeA) + "," + str(edgeB) + "," + str(newEdgeB) + "," + str(direction)


def getLengthOfEdge(edge):
    if edge[0] == None:
        return 0
    return edge[1] - edge[0] + 1


# walls can intersect. only care if inner areas intersect
def isAreaClear(roomList, roomA):
    for roomB in roomList:
        xOverlap = isRangeIntersect(roomA.left, roomA.right, roomB.left, roomB.right, False)
        yOverlap = isRangeIntersect(roomA.top, roomA.bottom, roomB.top, roomB.bottom, False)
        if xOverlap and yOverlap:
            return False
    return True

def isOnGrid(room):
    if room.top < 0 or room.bottom > MAXHEIGHT-1:
        return False
    if room.left < 0 or room.right > MAXWIDTH-1:
        return False
    return True


def createDoorFromAToB(start, stop, roomA, roomB, direction):
    global debugStr
    randomCoordinate = random.randint(start, stop)
    if direction == Direction.TOP:
        door = (randomCoordinate, roomA.top)
    elif direction == Direction.BOTTOM:
        door = (randomCoordinate, roomA.bottom)
    elif direction == Direction.LEFT:
        door = (roomA.left, randomCoordinate)
    else:
        door = (roomA.right, randomCoordinate)
    # debugStr += " Door: " + str(door)
    roomA.doors.append(door)
    roomB.doors.append(door)


class Room:
    def __init__(self):
        minWidth, maxWidth = 20, 40
        minHeight, maxHeight = 10, 15
        self.width = random.randint(minWidth, maxWidth)
        self.height = random.randint(minHeight, maxHeight)
        self.doors = []
        self.rectangleList = []

    # Offset of top left of room from 0,0
    # params x, y: Given based off offset from 0,0
    def setPosition(self, x, y):
        global debugStr
        self.left = x
        self.right = x + (self.width - 1)
        self.top = y
        self.bottom = y + (self.height - 1)
        # debugStr += " [" + str(self.left) + "," + str(self.right) + "," + str(self.top) + "," + str(self.bottom) + "] "

    def centerOnSide(self, direction, prevRoom):
        global debugStr
        prevEdgeCenter = prevRoom.getOuterEdgeCenter(direction)
        centerX, centerY = prevEdgeCenter
        if direction == Direction.TOP:
            x, y = centerX - (self.width/2), centerY - self.height + 1
        if direction == Direction.BOTTOM:
            x, y = centerX - (self.width/2), centerY
        if direction == Direction.LEFT:
            x, y = centerX - self.width + 1, centerY - (self.height/2)
        if direction == Direction.RIGHT:
            x, y = centerX, centerY - (self.height/2)        
        self.setPosition(int(x), int(y))

    def getOuterEdgeCenter(self, direction):
        global debugStr
        if direction == Direction.TOP:
            return (int(self.left+self.width/2), self.top)
        if direction == Direction.BOTTOM:
            return (int(self.left+self.width/2), self.bottom)
        if direction == Direction.LEFT:
            return (self.left, int(self.top+self.height/2))
        if direction == Direction.RIGHT:
            return (self.right, int(self.top+self.height/2))

    # Generic getEdge
    def getEdge(self, direction):
        if direction == Direction.TOP or direction == Direction.BOTTOM:
            return (self.left, self.right)
        else:
            return (self.top, self.bottom)



class ComplexRoom(Room):
    def __init__(self):
        global debugStr
        Room.__init__(self)
        # create initial rectangle
        rectangle = Rectangle()
        rectTopLeftX = random.randint(0, self.width - rectangle.width)
        rectTopLeftY = random.randint(0, self.height - rectangle.height)
        rectangle.setPosition(rectTopLeftX, rectTopLeftY)
        self.rectangleList.append(rectangle)
        self.left = rectangle.left
        self.right = rectangle.right
        self.top = rectangle.top
        self.bottom = rectangle.bottom
        self.leftYRange = [rectangle.top, rectangle.bottom]
        self.rightYRange = [rectangle.top, rectangle.bottom]
        self.topXRange = [rectangle.left, rectangle.right]
        self.bottomXRange = [rectangle.left, rectangle.right]
        # debugStr += "initrect: [" + str(rectangle.left) + "," + str(rectangle.right) + "," + str(rectangle.top) + "," + str(rectangle.bottom) + "] "

        # Place sub-rectangles that comprise of room
        i = 0
        while i < 30:
            rectangle = Rectangle()
            x = random.randint(0, self.width - rectangle.width)
            y = random.randint(0, self.height - rectangle.height)
            rectangle.setPosition(x, y)
            if rectangle.validIntersectWithOthers(self.rectangleList):
                self.rectangleList.append(rectangle)
                i += 1
                # debugStr += "rect: [" + str(rectangle.left) + "," + str(rectangle.right) + "," + str(rectangle.top) + "," + str(rectangle.bottom) + "] "

        # figure out edge ranges
        # TODO at the moment if rectangle edge shares same coordinate as "max" in that direction, will be ignored.
        # update so ranges are represented as sets and add new rectangle range to range set
        for rectangle in self.rectangleList:
            if rectangle.left < self.left:
                self.left = rectangle.left
                self.leftYRange = [rectangle.top, rectangle.bottom]
            # elif rectangle.left == self.left:
            #     # update leftYRange to include new rectangle
            #     self.leftYRange[0] = min(rectangle.top, self.leftYRange[0])
            #     self.leftYRange[1] = max(rectangle.bottom, self.leftYRange[1])
            if rectangle.right > self.right:
                self.right = rectangle.right
                self.rightYRange = [rectangle.top, rectangle.bottom]
            # elif rectangle.right == self.right:
            #     self.rightYRange[0] = min(rectangle.top, self.rightYRange[0])
            #     self.rightYRange[1] = max(rectangle.bottom, self.rightYRange[1])
            if rectangle.top < self.top:
                self.top = rectangle.top
                self.topXRange = [rectangle.left, rectangle.right]
            # elif rectangle.top == self.top:
            #     self.topXRange[0] = min(rectangle.left, self.topXRange[0])
            #     self.topXRange[1] = max(rectangle.right, self.topXRange[1])
            if rectangle.bottom > self.bottom:
                self.bottom = rectangle.bottom
                self.bottomXRange = [rectangle.left, rectangle.right]
            # elif rectangle.bottom == self.bottom:
            #     self.bottomXRange[0] = min(rectangle.left, self.bottomXRange[0])
            #     self.bottomXRange[1] = max(rectangle.right, self.bottomXRange[1])

        # Calculate offset so top and left start are 0, 0
        xOffset = 0 - self.left
        yOffset = 0 - self.top
        self.left = self.left + xOffset
        self.right = self.right + xOffset
        self.top = self.top + yOffset
        self.bottom = self.bottom + yOffset

        # shift over all rectangles using offest
        for rect in self.rectangleList:
            rect.left = rect.left + xOffset
            rect.right = rect.right + xOffset
            rect.top = rect.top + yOffset
            rect.bottom = rect.bottom + yOffset

        # update ranges with offset
        self.leftYRange = [self.leftYRange[0]+yOffset, self.leftYRange[1]+yOffset]
        self.rightYRange = [self.rightYRange[0]+yOffset, self.rightYRange[1]+yOffset]
        self.topXRange = [self.topXRange[0]+xOffset, self.topXRange[1]+xOffset]
        self.bottomXRange = [self.bottomXRange[0]+xOffset, self.bottomXRange[1]+xOffset]

        # update height and width
        self.height = (self.bottom - self.top) + 1
        self.width = (self.right - self.left) + 1


    # This will have to update the rectangles and edges as well
    # Offset of top left of room from 0,0
    def setPosition(self, x, y):
        global debugStr
        xOffset = x - self.left
        yOffset = y - self.top
        # update 4 outermost edges
        global debugStr
        self.left = x
        self.right = x + (self.width - 1)
        self.top = y
        self.bottom = y + (self.height - 1)

        # update edge ranges
        self.leftYRange = [self.leftYRange[0]+yOffset, self.leftYRange[1]+yOffset]
        self.rightYRange = [self.rightYRange[0]+yOffset, self.rightYRange[1]+yOffset]
        self.topXRange = [self.topXRange[0]+xOffset, self.topXRange[1]+xOffset]
        self.bottomXRange = [self.bottomXRange[0]+xOffset, self.bottomXRange[1]+xOffset]

        # debugStr += " room: [" + str(self.left) + "," + str(self.right) + "," + str(self.top) + "," + str(self.bottom) + "] "
        # debugStr += " roomEdges: [" + str(self.leftYRange) + "," + str(self.rightYRange) + "," + str(self.topXRange) + "," + str(self.bottomXRange) + "] "


    def getEdge(self, direction):
        if direction == Direction.TOP:
            return (self.topXRange[0], self.topXRange[1])
        if direction == Direction.BOTTOM:
            return (self.bottomXRange[0], self.bottomXRange[1])
        if direction == Direction.LEFT:
            return (self.leftYRange[0], self.leftYRange[1])
        if direction == Direction.RIGHT:
            return (self.rightYRange[0], self.rightYRange[1])



class Rectangle():
    def __init__(self, minWidth=3, maxWidth=8, minHeight=4, maxHeight=8):
        minWidth, maxWidth = minWidth, maxWidth
        minHeight, maxHeight = minHeight, maxHeight
        self.width = random.randint(minWidth, maxWidth)
        self.height = random.randint(minHeight, maxHeight)

    def setPosition(self, x, y):
        self.left = x
        self.top = y
        self.right = x + (self.width - 1)
        self.bottom = y + (self.height - 1)

    def validIntersectWithOthers(self, rectangleList):
        for roomB in rectangleList:
            lenXOverlap, lenOfYOverlap = 0, 0
            xOverlap = isRangeIntersect(self.left, self.right, roomB.left, roomB.right, False)
            if xOverlap:
                overlapEdge = (max(self.left, roomB.left), min(self.right, roomB.right))
                lenOfXOverlap = getLengthOfEdge(overlapEdge)
            yOverlap = isRangeIntersect(self.top, self.bottom, roomB.top, roomB.bottom, False)
            if yOverlap:
                overlapEdge = (max(self.top, roomB.top), min(self.bottom, roomB.bottom))
                lenOfYOverlap = getLengthOfEdge(overlapEdge)
            if (xOverlap and yOverlap) and (lenXOverlap > 2 or lenOfYOverlap > 2):
                return True
        return False

    def withinBounds(self, width, height):
        if self.right < width and self.bottom < height:
            return True
        return False


#################################
# Paint
#################################
def drawBoard(stdscr, grid, boardX, boardY):
    global debugStr
    for j, row in enumerate(grid):
        for i, cell in enumerate(row):
            x = boardX + i
            y = boardY + j
            if cell.subType == "grass":
                stdscr.addstr(y, x, ".", curses.color_pair(Colors.GRASS))
            elif cell.subType == "wall":
                stdscr.addstr(y, x, "#", curses.color_pair(Colors.WALL))
            elif cell.subType == "unlocked":
                stdscr.addstr(y, x, "+", curses.color_pair(Colors.WATER))
            elif cell.mainType == "background":
                stdscr.addstr(y, x, "", curses.color_pair(Colors.WALL))
            else:
                stdscr.addstr(y, x, cell, curses.color_pair(Colors.GRASS))


def draw(stdscr, grid):
    global debugStr
    # Clears the current screen
    stdscr.erase()

    drawBoard(stdscr, grid, 0, 0)
    # drawBoard(stdscr, newGrid, 100, 0)
    # drawBoard(stdscr, miniGrid1, 80, 0)
    # drawBoard(stdscr, miniGrid2, 120, 0)

    # Draw debug panel
    stdscr.addstr(50, 0, debugStr)

    # Paint 
    stdscr.refresh()

#################################
# Game Loop
#################################
def main(stdscr):
    global debugStr    
    # Settings for nCurses
    curses.curs_set(False)
    initColors()

    # init random seed
    # seed = time.time()
    seed = 1556925148.39278
    random.seed(seed)

    debugStr += str(seed)

    # grid, newGrid = generateRooms(stdscr)
    grid, _ = generateRooms(stdscr)

    # Game loop
    # draw(stdscr, grid, newGrid)
    draw(stdscr, grid)
    while True:
        key = stdscr.getch()
        if key in ActionMap:
            action = ActionMap[key]
            if action == Actions.QUIT:
                break
            draw(stdscr, grid)



#################################
# Helpers
#################################
class Actions(Enum):
    QUIT = 1
    
ActionMap = {
    ord("q"): Actions.QUIT
}

class Colors(IntEnum):
    TREE = 1
    WATER = 2
    GRASS = 3
    WALL = 4
    ITEMS = 5

def initColors():
    # pair number, fg, bg
    curses.init_pair(Colors.WATER, 39, 0)
    curses.init_pair(Colors.WALL, 7, 0)
    curses.init_pair(Colors.GRASS, 10, 0)
    curses.init_pair(Colors.ITEMS, 255, 0)



if __name__ == '__main__':
    # initialize curses
    curses.wrapper(main)