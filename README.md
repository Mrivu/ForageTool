# ForageTool
Submission for HY-TKT20019

This application is an addition to my D&D campaign, which allows players to search, discover and manage plants.

# Current state
- Admin users can add plant packages, which update the available plants for all users.
- Users are required to log in due to the existence of an admin account and database information.
- Users can view and sort all acquired plants.
- Users can view the catalogue, a list of all available plants.
- Admins can edit plants, and add additional information to them.
- Users can search for individual plants by name.
- The application displays statistics on found plants.
- Found plants can be sorted into different "Folders"


# Current state
- Currently, the application supports a login and register system. Users are seperated into Admins and regular users.
- Plant packages can be downloaded by admins via uploading a plant JSON. You can toggle if the download overrides any existing plants. 
- These plants are exported to the catalogue, a listing of all available plants. These plants can be further edited or removed.
- The catalogue also supports a search system, with a filter drop-down box based on which attribute the user wants to find the plant.
- The catalogue also orders the plants based on the given filter.
- The search keyword and filter are stored in the session for an easy user experience and reset once the user leaves the catalogue.
- The user can forage for plants, which are added to their inventory.
- The user can change user setting and see statistics form the profile panel.
- Folders can be created and added to the inventory.

# Guide
- Create database: 
```
$ sqlite3 database.db < schema.sql
```
- Initialize database:
```
$ sqlite3 database.db < init.sql
```
- Run application in /app:
```
$ flask run
```
- When importing plants, a valid plant JSON can be found under the plant Packages folder at "/ForageTool/PlantPackages/EvervastPlants2.json".

# Grading explanation
## Sovelluksen perusvaatimukset (7 p)
 - Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan tietokohteita - Pätee vain admineille
 - Käyttäjä pystyy valitsemaan tietokohteelle yhden tai useamman luokittelun - Kasvit luokitellaan ominaisuuksien perusteella, joita voi muokata. Kasvin harvinaisuuden voi kuitenkin valita etukäteen asetetuista arvoista.
 - Käyttäjä pystyy lähettämään lisätietoa tietokohteeseen - Käyttäjän inventaarioon voidaan luoda kansioita

## Sovelluksen turvallisuus (20 p)
Lomakkeissa on estetty CSRF-aukko	2 p	- Koodasin CSRF tarkistuksen, mutten onnistunut sen testauksessa