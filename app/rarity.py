RarityByID = {
    "Common" : 1,
    "Uncommon" : 2,
    "Rare": 3,
    "Very Rare": 4,
    "Legendary": 5,
}

def check_rarity(rarity):
    if rarity in RarityByID:
        return RarityByID[rarity]
    else:
        return -1
    

rollResults = [
    {"Roll": 1, "Common": 0, "Uncommon": 0, "Rare": 0, "Very Rare": 0, "Legendary": 0},
    {"Roll": 2, "Common": 0, "Uncommon": 0, "Rare": 0, "Very Rare": 0, "Legendary": 0},
    {"Roll": 3, "Common": 0, "Uncommon": 0, "Rare": 0, "Very Rare": 0, "Legendary": 0},
    {"Roll": 4, "Common": 0, "Uncommon": 0, "Rare": 0, "Very Rare": 0, "Legendary": 0},
    {"Roll": 5, "Common": 0, "Uncommon": 0, "Rare": 0, "Very Rare": 0, "Legendary": 0},
    {"Roll": 6, "Common": 0, "Uncommon": 0, "Rare": 0, "Very Rare": 0, "Legendary": 0},
    {"Roll": 7, "Common": 0, "Uncommon": 0, "Rare": 0, "Very Rare": 0, "Legendary": 0},
    {"Roll": 8, "Common": 0, "Uncommon": 0, "Rare": 0, "Very Rare": 0, "Legendary": 0},
    {"Roll": 9, "Common": 0, "Uncommon": 0, "Rare": 0, "Very Rare": 0, "Legendary": 0},
    {"Roll": 10, "Common": 0, "Uncommon": 0, "Rare": 0, "Very Rare": 0, "Legendary": 0},
    {"Roll": 11, "Common": 100, "Uncommon": 0, "Rare": 0, "Very Rare": 0, "Legendary": 0},
    {"Roll": 12, "Common": 100, "Uncommon": 0, "Rare": 0, "Very Rare": 0, "Legendary": 0},
    {"Roll": 13, "Common": 100, "Uncommon": 0, "Rare": 0, "Very Rare": 0, "Legendary": 0},
    {"Roll": 14, "Common": 91, "Uncommon": 9, "Rare": 0, "Very Rare": 0, "Legendary": 0},
    {"Roll": 15, "Common": 90, "Uncommon": 10, "Rare": 0, "Very Rare": 0, "Legendary": 0},
    {"Roll": 16, "Common": 89, "Uncommon": 11, "Rare": 0, "Very Rare": 0, "Legendary": 0},
    {"Roll": 17, "Common": 81, "Uncommon": 12, "Rare": 7, "Very Rare": 0, "Legendary": 0},
    {"Roll": 18, "Common": 79, "Uncommon": 13, "Rare": 8, "Very Rare": 0, "Legendary": 0},
    {"Roll": 19, "Common": 77, "Uncommon": 14, "Rare": 9, "Very Rare": 0, "Legendary": 0},
    {"Roll": 20, "Common": 70, "Uncommon": 15, "Rare": 10, "Very Rare": 5, "Legendary": 0},
    {"Roll": 21, "Common": 67, "Uncommon": 16, "Rare": 11, "Very Rare": 6, "Legendary": 0},
    {"Roll": 22, "Common": 64, "Uncommon": 17, "Rare": 12, "Very Rare": 7, "Legendary": 0},
    {"Roll": 23, "Common": 61, "Uncommon": 18, "Rare": 13, "Very Rare": 8, "Legendary": 0},
    {"Roll": 24, "Common": 58, "Uncommon": 19, "Rare": 14, "Very Rare": 9, "Legendary": 0},
    {"Roll": 25, "Common": 54, "Uncommon": 20, "Rare": 15, "Very Rare": 10, "Legendary": 1},
    {"Roll": 26, "Common": 50, "Uncommon": 21, "Rare": 16, "Very Rare": 11, "Legendary": 2},
    {"Roll": 27, "Common": 46, "Uncommon": 22, "Rare": 17, "Very Rare": 12, "Legendary": 3},
    {"Roll": 28, "Common": 42, "Uncommon": 23, "Rare": 18, "Very Rare": 13, "Legendary": 4},
    {"Roll": 29, "Common": 38, "Uncommon": 24, "Rare": 19, "Very Rare": 14, "Legendary": 5},
    {"Roll": 30, "Common": 35, "Uncommon": 25, "Rare": 20, "Very Rare": 15, "Legendary": 5},
    {"Roll": 31, "Common": 32, "Uncommon": 26, "Rare": 21, "Very Rare": 15, "Legendary": 6},
    {"Roll": 32, "Common": 29, "Uncommon": 27, "Rare": 22, "Very Rare": 16, "Legendary": 6},
    {"Roll": 33, "Common": 27, "Uncommon": 28, "Rare": 23, "Very Rare": 16, "Legendary": 6},
    {"Roll": 34, "Common": 23, "Uncommon": 29, "Rare": 24, "Very Rare": 17, "Legendary": 7},
    {"Roll": 35, "Common": 21, "Uncommon": 30, "Rare": 25, "Very Rare": 17, "Legendary": 7},
    {"Roll": 36, "Common": 17, "Uncommon": 31, "Rare": 26, "Very Rare": 18, "Legendary": 8},
    {"Roll": 37, "Common": 15, "Uncommon": 32, "Rare": 27, "Very Rare": 18, "Legendary": 8},
    {"Roll": 38, "Common": 11, "Uncommon": 33, "Rare": 28, "Very Rare": 19, "Legendary": 9},
    {"Roll": 39, "Common": 9, "Uncommon": 34, "Rare": 29, "Very Rare": 19, "Legendary": 9},
    {"Roll": 40, "Common": 5, "Uncommon": 35, "Rare": 30, "Very Rare": 20, "Legendary": 10},
]

## Any rolls above 40 will be treaeted as a 40.