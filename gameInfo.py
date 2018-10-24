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

levelInfo = {
    0: {
        "itemCounts": {
            "weapons": (1, 2),
            "monsters": (2, 3),
        },
        "portals": (1, 2),
    }
}

randomLevelItems = {
    0: {
        "weapons": ["bow", "sword"],
        "weaponWeight": [0.45, 0.45],
        "monsters": ["orc", "uruk-hai"],
        "monsterWeight": [0.5, 0.5]
    },
    1: {
        # "monsters": ["cow", "uruk-hai"]
    }
}

# if only want one of a item, these lists are exclusive from random. Otherwise,
# lists can share items
requiredLevelItems = {
    0: ["sword"],
}


# Should regenerate board everytime leave board? So if you don't pick up an item, it may disappear forever?
