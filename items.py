from enum import Enum, IntEnum

class MainType(Enum):
    BACKGROUND = 1
    TERRAIN = 2
    EDIBLES = 3
    MONSTER = 4
    DOOR = 5

class SubType(Enum):
    BACKGROUND = 1
    GRASS = 2
    WALL = 3
    WATER = 4
    APPLE = 5
    MONSTER = 6
    UNLOCKED = 7

class BoardCell:
    boardCellNextId = 0
    def __init__(self, mainType, subType):
        self.id = self.boardCellNextId
        BoardCell.boardCellNextId += 1
        self.mainType = mainType
        self.subType = subType
