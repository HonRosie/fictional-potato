from enum import Enum, IntEnum

class Type(Enum):
    TERRAIN = 1
    DOOR = 2
    WEAPON = 3

class Terrain(Enum):
    BACKGROUND = 1
    GRASS = 2
    WALL = 3
    WATER = 4
    UNLOCKED = 5

class Weapon(Enum):
    SWORD = 1

class BoardCell:
    boardCellNextId = 0
    def __init__(self, mainType, subType):
        self.id = self.boardCellNextId
        BoardCell.boardCellNextId += 1
        self.mainType = mainType
        self.subType = subType
