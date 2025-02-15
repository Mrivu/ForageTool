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