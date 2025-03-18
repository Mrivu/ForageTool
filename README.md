# ForageTool
This application is an addition to my D&D campaign, which allows players to search, discover and manage plants.

## User Guide
This section is for non-admin users, who use the website.
- Feel free to contact us at "ivugames@outlook.fi" regarding any bugs or issues.

## Forage and Alchemy ruleset
The ruleset is being overhauled.

### Plant logic
Your roll determines the probabilities of plant rarity. See rarity.py for the exact levels.
The amount of plants you find is calculated in the following way:
```
(floor(Diceroll+Bonus+(extra 1 on crit)) + availability) * multiplier
```

## Setup
This is a guide for a local setup for custom use. We are, however, working on custom worlds for the website.
- Clone the repository:
```
$ git clone https://github.com/Mrivu/ForageTool.git
```
- Create database:
```
$ sqlite3 database.db < schema.sql
```
- Initialize database:
```
$ sqlite3 database.db < init.sql
```
- Setup ForageTool/app/config.py:
Set an appropriate secret_key and enter the desired route for the forageTool.
- Run application in ForageTool/app:
```
$ flask run
```
- When importing plants, a valid plant JSON can be found under the plant Packages folder at "ForageTool/PlantPackages/EvervastPlants2.json".

## Help
### "Invalid manual import file. See the github for help."
The structure of the import file is invalid. Please see the example json file in "ForageTool/app/InventoryImport/Plants.json". This error is raised when the attributes "count" and/or "plantName" are not found at any given entry.

### "Invalid plant in import. See the github for help."
A plant you tried to import was Invalid. Please see the example json file in "ForageTool/PlantPackages/EvervastPlants2.json". This error is raised when one of the plant's attributes is not found at any given entry.

## Plant flags
### Unobtainable
This plant is unobtainable via Forage rolls.
### Hidden
This plant is not found in the catalogue, unless the user has admin status.
### Secret
This plant's critical information is hidden until the user finds one.

## Admin console
The admin console is only accessible if you run the application locally using your own database. The documentation is placed within.
- Run the console in ForageTool/app:
```
$ python3 adminconsole.py
```

# Submission for HY-TKT20019

## Current state
- Currently, the application supports a login and register system. Users are separated into Admins and regular users.
- Plant packages can be downloaded by admins via uploading a plant JSON. You can toggle if the download overrides any existing plants.
- These plants are exported to the catalogue, a listing of all available plants. These plants can be further edited or removed.
- The catalogue also supports a search system, with a filter drop-down box based on which attribute the user wants to find the plant.
- The catalogue also orders the plants based on the given filter.
- The search keyword and filter are stored in the session for an easy user experience and reset once the user leaves the catalogue.
- The user can forage for plants, which are added to their inventory.
- The user can change user settings and see statistics from the profile panel.
- Folders can be created and added to the inventory.

## Grading explanation
### Sovelluksen perusvaatimukset (7 p)
- Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan tietokohteita - Pätee vain admineille
- Käyttäjä pystyy valitsemaan tietokohteelle yhden tai useamman luokittelun - Kasvit luokitellaan ominaisuuksien perusteella, joita voi muokata. Kasvin harvinaisuuden voi kuitenkin valita etukäteen asetetuista arvoista.
- Käyttäjä pystyy lähettämään lisätietoa tietokohteeseen - Käyttäjän inventaarioon voidaan luoda kansioita

### Sovelluksen turvallisuus (20 p)
Lomakkeissa on estetty CSRF-aukko   2 p - Koodasin CSRF tarkistuksen, mutten onnistunut sen testauksessa