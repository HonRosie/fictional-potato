# Key: ASCII character -> mainType
"""
@ hero
### terrain ###
. grass
# unexplored area
~ water
- wall
< stairs up
> stairs down
+ portal
### monster ###
a-z monsters
### items ###
% chest
! potion
' scrolls
? books
^ keys
* edible
| weapon
& armour
skill item (ie. glasses)
"""

# Counts do not include any super special board items
levelInfo = {
    0: {
        "boards": ["main", "farm"],
        "itemCount": {
            "weapons": 5,
        }
    }
}

# Required and random are exclusive lists
randomLevelItems = {
    0: {
        "weapons": ["bow", "sword"],
    }
}

# if only want one of a item, these lists are exclusive from random. Otherwise,
# lists can share items
requiredLevelItems = {
    0: {
        "weapons": ["sword"]
    }
}

# Items required for a specific board
requiredBoardItems = {
    "farm": {
        # "monsters": ["cow"]
    }
}

# Should regenerate board everytime leave board? So if you don't pick up an item, it may disappear forever?
