CREATE TABLE users (
    userID INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password_hash TEXT,
    isAdmin INTEGER,
    forageBonus INTEGER,
    forageMultiplier INTEGER
);

CREATE TABLE statistics (
    userID INTEGER PRIMARY KEY,
    timesForaged INTEGER DEFAULT 0,
    highestRarity TEXT DEFAULT "None",
    FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE
);

CREATE TABLE inventory (
    userID INTEGER,
    plantName TEXT,
    quantity INTEGER,
    PRIMARY KEY (userID, plantName),
    FOREIGN KEY (plantName) REFERENCES plants(plantName) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE
);

CREATE TABLE folders (
    folderID INTEGER PRIMARY KEY AUTOINCREMENT,
    userID INTEGER,
    folderName TEXT,
    UNIQUE(userID, folderName),
    FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE
);

CREATE TABLE folder (
    folderID INTEGER,
    plantName TEXT,
    quantity INTEGER DEFAULT 1,
    PRIMARY KEY (folderID, plantName),
    FOREIGN KEY (folderID) REFERENCES folders(folderID) ON DELETE CASCADE,
    FOREIGN KEY (plantName) REFERENCES plants(plantName) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE plants (
    plantID INTEGER,
    plantName TEXT PRIMARY KEY,
    plantDescription TEXT,
    rarityID INTEGER,
    unobtainable INTEGER DEFAULT 0, --Cannot be found while Foraging
    isHidden INTEGER DEFAULT 0, --Not Shown in catalogue
    isSecret INTEGER DEFAULT 0 --Name Replaced with ??? until found
);

CREATE TABLE found (
    plantName TEXT,
    userID INTEGER,
    PRIMARY KEY (plantName, userID),
    FOREIGN KEY (plantName) REFERENCES plants(plantName) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE
);

CREATE TABLE rarity (
    rarityID INTEGER PRIMARY KEY,
    rarity TEXT
);

CREATE TABLE areas (
    areaName TEXT PRIMARY KEY
);
CREATE TABLE regions (
    regionName TEXT PRIMARY KEY
);
CREATE TABLE effects (
    effectName TEXT PRIMARY KEY
);

CREATE TABLE area (
    plantName TEXT,
    areaName TEXT,
    PRIMARY KEY (plantName, areaName),
    FOREIGN KEY (plantName) REFERENCES plants (plantName) ON DELETE CASCADE,
    FOREIGN KEY (areaName) REFERENCES areas (areaName) 
);

CREATE TABLE region (
    plantName TEXT,
    regionName TEXT,
    PRIMARY KEY (plantName, regionName),
    FOREIGN KEY (plantName) REFERENCES plants (plantName) ON DELETE CASCADE,
    FOREIGN KEY (regionName) REFERENCES regions (regionName)
);

CREATE TABLE effect (
    repeats INTEGER,
    plantName TEXT,
    effectName TEXT,
    PRIMARY KEY (plantName, effectName, repeats),
    FOREIGN KEY (plantName) REFERENCES plants (plantName) ON DELETE CASCADE,
    FOREIGN KEY (effectName) REFERENCES effects (effectName)
);