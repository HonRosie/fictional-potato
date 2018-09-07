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


# Items required for a specific board
requiredBoardItems = {
    "main": {
        "weapon": ["sword"],
    },
    "farm": {
    }
}

# Should regenerate board everytime leave board? So if you don't pick up an item, it may disappear forever?
