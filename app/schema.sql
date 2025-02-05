CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    admin BOOLEAN
);

CREATE TABLE "plants" (
	"Name"	INTEGER,
	"Rarity"	TEXT,
	"Area"	TEXT,
	"Region"	TEXT,
	"Effects"	TEXT,
	"Description"	TEXT
)