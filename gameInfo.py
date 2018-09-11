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
        "height": (20, 30),
        "width": (50, 70),
        # Items with multiple possible subtypes
        "itemCounts": {
            "weapons": (1, 3),
            "monsters": (2, 3),
        },
        "portals": (1, 2),
    }
}

randomLevelItems = {
    0: {
        "weapons": ["bow", "sword"],
        "monsters": ["orc", "uruk-hai"]
    },
    1: {
        # "monsters": ["cow", "uruk-hai"]
    }
}

# if only want one of a item, these lists are exclusive from random. Otherwise,
# lists can share items
# requiredLevelItems = {
#     0: {
#         "weapons": ["sword"]
#     },
#     1: {
#         "cow":
#     }
# }


# Should regenerate board everytime leave board? So if you don't pick up an item, it may disappear forever?
