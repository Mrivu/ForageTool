CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password_hash TEXT,
    isAdmin INTEGER
);

CREATE TABLE plants (
    plantName TEXT PRIMARY KEY,
    rarity TEXT,
    rarityID INTEGER,
    plantDescription TEXT
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
    FOREIGN KEY (plantName) REFERENCES plants (plantName),
    FOREIGN KEY (areaName) REFERENCES areas (areaName)
);

CREATE TABLE region (
    plantName TEXT,
    regionName TEXT,
    PRIMARY KEY (plantName, regionName),
    FOREIGN KEY (plantName) REFERENCES plants (plantName),
    FOREIGN KEY (regionName) REFERENCES regions (regionName)
);

CREATE TABLE effect (
    repeats INTEGER,
    plantName TEXT,
    effectName TEXT,
    PRIMARY KEY (plantName, effectName, repeats),
    FOREIGN KEY (plantName) REFERENCES plants (plantName),
    FOREIGN KEY (effectName) REFERENCES effects (effectName)
);